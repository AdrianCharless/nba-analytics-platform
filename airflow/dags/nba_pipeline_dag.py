from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.databricks.operators.databricks import DatabricksNotebookOperator
from datetime import datetime
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator

default_args = {
    "owner": "adrian",
    "retries": 0,
}

with DAG(
    dag_id="nba_analytics_pipeline",
    default_args=default_args,
    description="NBA data pipeline: Kafka ingestion -> Bronze -> Silver -> Gold",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["nba", "portfolio"],
) as dag:

    produce_data = DockerOperator(
        task_id="produce_nba_data",
        image="nba-analytics-platform-nba-producer",
        container_name="airflow-nba-producer",
        api_version="auto",
        auto_remove="success",
        docker_url="unix://var/run/docker.sock",
        network_mode="kafka_default",
        environment={
            "KAFKA_BROKER": "kafka:29092",
        },
    )

    consume_data = DockerOperator(
        task_id="consume_nba_data",
        image="nba-analytics-platform-nba-consumer",
        container_name="airflow-nba-consumer",
        api_version="auto",
        auto_remove="success",
        docker_url="unix://var/run/docker.sock",
        network_mode="kafka_default",
        environment={
            "DATABRICKS_HOST": "{{ var.value.DATABRICKS_HOST }}",
            "DATABRICKS_TOKEN": "{{ var.value.DATABRICKS_TOKEN }}",
            "KAFKA_BROKER": "kafka:29092",
        },
    )

    job_cluster_spec = {
    "spark_version": "15.4.x-scala2.12",
    "node_type_id": "m5d.large",
    "num_workers": 0,
    "spark_conf": {
        "spark.databricks.cluster.profile": "singleNode",
        "spark.master": "local[*]"
    },
    "custom_tags": {
        "ResourceClass": "SingleNode"
    }
}

    transform_silver = DatabricksSubmitRunOperator(
        task_id="transform_silver",
        databricks_conn_id="databricks_default",
        json={
            "run_name": "transform_silver_run",
            "tasks": [
                {
                    "task_key": "transform_silver_task",
                    "notebook_task": {
                        "notebook_path": "/Users/anuragcharles@yahoo.ca/02_silver_transform",
                        "source": "WORKSPACE",
                    },
                }
            ],
        },
    )

    aggregate_gold = DatabricksSubmitRunOperator(
        task_id="aggregate_gold",
        databricks_conn_id="databricks_default",
        json={
            "run_name": "aggregate_gold_run",
            "tasks": [
                {
                    "task_key": "aggregate_gold_task",
                    "notebook_task": {
                        "notebook_path": "/Users/anuragcharles@yahoo.ca/03_gold_aggregation",
                        "source": "WORKSPACE",
                    },
                }
            ],
        },
    )

    produce_data >> consume_data >> transform_silver >> aggregate_gold