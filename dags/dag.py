import os
from airflow.decorators import dag, task
from datetime import datetime, timedelta
import feast
from feast import RepoConfig, FeatureStore
import pendulum
from pathlib import Path


@dag(
    schedule="@hourly",  # Adjust the schedule as needed
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    tags=["feast"],
)
def materialize_dag():
    @task()
    def materialize():
        repo_path = '/opt/airflow/feature_repo/'
        
        # Use FeatureStore with explicit repo_path
        store = FeatureStore(repo_path=repo_path)
        
        # Calculate start and end time for materialization
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        print(f"Materializing data from {start_time} to {end_time}")
        
        # Materialize the previous hour of data
        store.materialize(start_time, end_time)

    materialize()


# This line is required for Airflow to properly register the DAG
materialize_dag = materialize_dag()