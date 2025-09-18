FROM apache/airflow:2.10.3-python3.11
USER airflow
ENV PATH="/home/airflow/.local/bin:${PATH}"
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install apache-airflow-providers-databricks>=6.0.0 \
    && pip install apache-airflow-providers-microsoft-azure>=8.3.0 \
    && pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /opt/airflow
COPY airflow.cfg /opt/airflow/airflow.cfg
COPY k8s/pod-template.yaml /opt/airflow/pod_template.yaml
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/