from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from azure.identity import DefaultAzureCredential
from airflow.models import Variable
from datetime import datetime, timedelta
import requests
import pandas as pd
import adlfs
import time
import logging

# ----------------------------
# CONFIGURATION
# ----------------------------
RAW_HIST_PATH = "raw/historical/hourly_data.parquet"
RAW_DAILY_PATH = "raw/daily/hourly_data.parquet"
PROC_PATH = "processed/curated.parquet"
PRED_PATH = "predictions/"

ACCOUNT_NAME = "mlopsadlsvs5tyf"
MODEL_NAME = "nyis_forecast"
MLFLOW_URI = "http://mlflow:5000"

# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------
def build_eia_url(api_key, start_date, end_date):
    return (
        f"https://api.eia.gov/v2/electricity/rto/region-data/data/"
        f"?api_key={api_key}&frequency=hourly"
        f"&data[0]=value"
        f"&facets[respondent][]=NYIS"
        f"&sort[0][column]=period&sort[0][direction]=desc"
        f"&start={start_date}&end={end_date}&offset=0&length=5000"
    )

def safe_requests_get(url, retries=3, backoff=5):
    for i in range(retries):
        try:
            r = requests.get(url)
            r.raise_for_status()
            return r
        except Exception as e:
            logging.warning(f"Request failed ({i+1}/{retries}): {e}")
            time.sleep(backoff * (i+1))
    raise RuntimeError(f"Failed to fetch URL after {retries} attempts: {url}")

def safe_read_parquet(path, fs):
    try:
        return pd.read_parquet(path, filesystem=fs)
    except FileNotFoundError:
        logging.info(f"{path} not found. Creating new DataFrame.")
        return pd.DataFrame()

# ----------------------------
# TASK FUNCTIONS
# ----------------------------
# Use DefaultAzureCredential everywhere
credential = DefaultAzureCredential()

def fetch_historical_data(**kwargs):
    fs = adlfs.AzureBlobFileSystem(account_name=ACCOUNT_NAME, credential=credential)
    api_key = Variable.get("EIAApiToken")
    start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
    url = build_eia_url(api_key, start_date, end_date)
    
    r = safe_requests_get(url)
    df = pd.DataFrame(r.json()["response"]["data"])
    df.to_parquet(RAW_HIST_PATH, filesystem=fs, index=False)
    logging.info(f"Historical data saved to {RAW_HIST_PATH}, {len(df)} rows.")

def fetch_daily_block(**kwargs):
    fs = adlfs.AzureBlobFileSystem(account_name=ACCOUNT_NAME, credential=credential)
    api_key = Variable.get("EIAApiToken")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = build_eia_url(api_key, yesterday, yesterday)
    
    r = safe_requests_get(url)
    df_new = pd.DataFrame(r.json()["response"]["data"])
    
    df_old = safe_read_parquet(RAW_DAILY_PATH, fs)
    df = pd.concat([df_old, df_new]).drop_duplicates()
    
    df.to_parquet(RAW_DAILY_PATH, filesystem=fs, index=False)
    logging.info(f"Daily data saved to {RAW_DAILY_PATH}, {len(df)} rows.")

def preprocess_data(**kwargs):
    fs = adlfs.AzureBlobFileSystem(account_name=ACCOUNT_NAME, credential=credential)
    
    hist_df = safe_read_parquet(RAW_HIST_PATH, fs)
    daily_df = safe_read_parquet(RAW_DAILY_PATH, fs)
    
    if hist_df.empty and daily_df.empty:
        logging.warning("No data to preprocess")
        return
    
    df = pd.concat([hist_df, daily_df]).drop_duplicates().sort_values("period")
    df["datetime"] = pd.to_datetime(df["period"])
    df["hour"] = df["datetime"].dt.hour
    df["dayofweek"] = df["datetime"].dt.dayofweek
    df["lag_1h"] = df["value"].shift(1)
    df.dropna(inplace=True)
    
    df.to_parquet(PROC_PATH, filesystem=fs, index=False)
    logging.info(f"Preprocessed data saved to {PROC_PATH}, {len(df)} rows.")

def compare_forecast_vs_actual(**kwargs):
    fs = adlfs.AzureBlobFileSystem(account_name=ACCOUNT_NAME, credential=credential)
    df = safe_read_parquet(PRED_PATH, fs)
    if df.empty or "forecast" not in df.columns or "value" not in df.columns:
        logging.info("No valid predictions found.")
        return
    
    rmse = ((df["forecast"] - df["value"]) ** 2).mean() ** 0.5
    logging.info(f"Forecast RMSE: {rmse}")
    if rmse > 5000:
        return "trigger_weekly_retrain"

# ----------------------------
# DAG ARGUMENTS
# ----------------------------
default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ----------------------------
# DAILY DAG
# ----------------------------
with DAG(
    "energy_daily_ingestion",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=datetime(2025, 9, 1),
    catchup=False,
    max_active_runs=1,
) as daily_dag:

    historical_task = PythonOperator(
        task_id="fetch_historical_data",
        python_callable=fetch_historical_data,
    )

    daily_task = PythonOperator(
        task_id="fetch_daily_block",
        python_callable=fetch_daily_block,
    )

    preprocess_task = PythonOperator(
        task_id="preprocess_data",
        python_callable=preprocess_data,
    )

    monitor_task = PythonOperator(
        task_id="compare_forecast_vs_actual",
        python_callable=compare_forecast_vs_actual,
    )

    trigger_weekly = TriggerDagRunOperator(
        task_id="trigger_weekly_retrain",
        trigger_dag_id="energy_weekly_retrain",
        wait_for_completion=False,
    )

    historical_task >> preprocess_task
    daily_task >> preprocess_task >> monitor_task >> trigger_weekly

# ----------------------------
# WEEKLY DAG
# ----------------------------
with DAG(
    "energy_weekly_retrain",
    default_args=default_args,
    schedule_interval="@weekly",
    start_date=datetime(2025, 9, 1),
    catchup=False,
    max_active_runs=1,
) as weekly_dag:

    retrain = DatabricksSubmitRunOperator(
        task_id="train_model_on_databricks",
        databricks_conn_id="databricks_default",
        existing_cluster_id="mlops-cluster",
        notebook_task={
            "notebook_path": "/Workspace/Shared/energy_forecast",
            "base_parameters": {
                "input_path": PROC_PATH,
                "model_name": MODEL_NAME,
                "mlflow_uri": MLFLOW_URI,
                "pred_path": PRED_PATH,
            },
        },
    )
