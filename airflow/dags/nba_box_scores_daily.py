import sys, pendulum
from datetime import timedelta
from airflow.decorators import dag, task

sys.path.insert(0, "/opt/airflow/project")


@dag(
    dag_id="nba_box_scores_daily",
    schedule="0 9 * * *",
    start_date=pendulum.datetime(2026, 10, 20, tz="America/Toronto"),
    catchup=True,
    max_active_runs=1,
    default_args={
        "retries": 3, 
        "retry_delay": timedelta(minutes=15),
        "execution_timeout": timedelta(minutes=10),
        },
    tags=["box_scores"],
)
def nba_box_scores_daily():

    @task
    def fetch(ds=None):
        from datetime import date
        from fetch_box_scores import fetch_box_scores
        return str(fetch_box_scores(date.fromisoformat(ds)))

    @task
    def parse():
        from parse_box_scores import parse_box_scores
        return parse_box_scores()

    fetch() >> parse()


nba_box_scores_daily()