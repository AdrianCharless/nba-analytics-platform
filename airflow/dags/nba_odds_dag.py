import sys, pendulum
from datetime import timedelta
from airflow.decorators import dag, task

sys.path.insert(0, "/opt/airflow/project")


@dag(
    dag_id="nba_odds_daily",
    schedule="0 12,18 * * *",
    start_date=pendulum.datetime(2026, 11, 1, tz="America/Toronto"),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["odds"],
)
def nba_odds_daily():

    @task
    def fetch():
        from fetch_odds import fetch_odds
        return str(fetch_odds())

    @task
    def parse():
        from parse_odds import parse_odds
        return parse_odds()

    fetch() >> parse()


nba_odds_daily()