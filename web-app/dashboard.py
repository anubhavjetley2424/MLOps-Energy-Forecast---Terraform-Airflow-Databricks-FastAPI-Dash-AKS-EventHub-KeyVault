import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ===========================
# CONFIG
# ===========================
EIA_API_KEY = "FdwtmoZBc5A54ZXbXIraRU5ZUmrOw1Fxl5cEOAyz"
MLFLOW_API_URL = "http://4.237.165.127:5000/invocations"

# ===========================
# UTILITY FUNCTIONS
# ===========================
def fetch_last_24h_data():
    """Fetch last 24 hours of NYIS demand data from EIA API."""
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    url = (
        f"https://api.eia.gov/v2/electricity/rto/region-data/data/"
        f"?api_key={EIA_API_KEY}&frequency=hourly"
        f"&data[0]=value"
        f"&facets[respondent][]=NYIS"
        f"&sort[0][column]=period&sort[0][direction]=desc"
        f"&start={yesterday}&end={today}&offset=0&length=5000"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()["response"]["data"]
    df = pd.DataFrame(data)
    df["period"] = pd.to_datetime(df["period"])
    df = df.sort_values("period").reset_index(drop=True)

    # Map value to required features for ML model
    df["DF"] = df["value"]
    df["NG"] = df["value"]
    df["TI"] = 0  # placeholder if TI not available

    return df

def add_features(df):
    """Add lags, hour, dayofweek for ML model."""
    df["hour"] = df["period"].dt.hour
    df["dayofweek"] = df["period"].dt.dayofweek
    
    for lag in range(1, 25):
        df[f"lag_D_{lag}"] = df["value"].shift(lag)
        df[f"lag_DF_{lag}"] = df["DF"].shift(lag)
    
    df.dropna(inplace=True)

    FEATURES = ["DF", "NG", "TI", "hour", "dayofweek"]
    for lag in range(1, 25):
        FEATURES += [f"lag_D_{lag}", f"lag_DF_{lag}"]
    return df, FEATURES

# ===========================
# DASH APP
# ===========================
app = dash.Dash(__name__)

app.layout = html.Div(
    style={
        "backgroundColor": "#0e0e0e",
        "color": "#ffffff",
        "fontFamily": "Arial, Helvetica, sans-serif",
        "padding": "20px"
    },
    children=[
        html.H2("NYIS Energy Forecast Dashboard", style={"textAlign": "center", "color": "#00ffcc"}),
        dcc.Graph(id="forecast-graph"),
        html.Button(
            "Run Forecast",
            id="predict-btn",
            n_clicks=0,
            style={
                "backgroundColor": "#00ffcc",
                "color": "#0e0e0e",
                "border": "none",
                "padding": "10px 20px",
                "margin": "10px 0",
                "cursor": "pointer",
                "fontSize": "16px",
                "borderRadius": "5px"
            }
        ),
        html.Div(id="prediction-output", style={"marginTop": "10px", "fontSize": "16px"})
    ]
)

@app.callback(
    [Output("forecast-graph", "figure"),
     Output("prediction-output", "children")],
    [Input("predict-btn", "n_clicks")]
)
def update_forecast(n_clicks):
    fig = go.Figure()
    prediction_text = "Click 'Run Forecast' to generate 3-hour predictions."

    try:
        # Fetch last 24h data and prepare features
        df = fetch_last_24h_data()
        df, FEATURES = add_features(df)

        # Plot historical demand
        fig.add_trace(go.Scatter(
            x=df["period"], y=df["value"],
            mode="lines+markers",
            name="Historical Demand",
            line=dict(color="#00aaff", width=2),
            marker=dict(size=6)
        ))

        if n_clicks > 0:
            last_row = df.iloc[-1].copy()
            preds = []
            future_times = []

            for i in range(3):  # predict next 3 hours
                payload = {"dataframe_records": [last_row[FEATURES].astype(float).to_dict()]}

                # Print payload for debugging
                print("Sending payload to MLflow API:")
                print(payload)

                res = requests.post(MLFLOW_API_URL, json=payload)
                res.raise_for_status()
                pred = res.json()["predictions"][0]
                preds.append(pred)

                next_time = last_row["period"] + pd.Timedelta(hours=1)
                future_times.append(next_time)

                # Update last_row for next prediction
                last_row["period"] = next_time
                last_row["hour"] = next_time.hour
                last_row["dayofweek"] = next_time.dayofweek

                for lag in range(24, 1, -1):
                    last_row[f"lag_D_{lag}"] = last_row[f"lag_D_{lag-1}"]
                    last_row[f"lag_DF_{lag}"] = last_row[f"lag_DF_{lag-1}"]
                last_row["lag_D_1"] = pred
                last_row["lag_DF_1"] = last_row["DF"]

            # Plot forecast
            fig.add_trace(go.Scatter(
                x=future_times, y=preds,
                mode="lines+markers",
                name="3-Hour Forecast",
                line=dict(color="#ff3300", width=2, dash="dot"),
                marker=dict(size=8)
            ))
            prediction_text = "Generated 3-hour forecast using real EIA data."

    except Exception as e:
        prediction_text = f"Error fetching data or predicting: {e}"

    fig.update_layout(
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#0e0e0e",
        font=dict(color="#ffffff", family="Arial, Helvetica, sans-serif"),
        title=dict(text="NYIS Energy Demand Forecast", font=dict(size=24, color="#00ffcc")),
        xaxis=dict(title="Time", gridcolor="#333333"),
        yaxis=dict(title="Demand (MW)", gridcolor="#333333"),
        legend=dict(bgcolor="#0e0e0e", font=dict(color="#ffffff"))
    )

    return fig, prediction_text

# ===========================
# Keep run() as requested
# ===========================
if __name__ == "__main__":
    app.run(debug=True)
