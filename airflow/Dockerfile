FROM apache/airflow:2.11.0

RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    apache-airflow-providers-docker \
    apache-airflow-providers-databricks \
    pandas \
    pyarrow \
    python-dotenv \
    requests