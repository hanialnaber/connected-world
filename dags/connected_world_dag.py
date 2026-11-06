"""Airflow DAG for Connected World: extract -> dbt build (models + tests) -> publish.

Mirrors `python -m pipeline all --refresh`. Each step is idempotent: extract re-downloads and
rewrites bronze, dbt rebuilds the warehouse, and publish only runs if every data test passed.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT = Path(__file__).resolve().parents[1]


def _extract(**_):
    from pipeline import extract
    extract.run(refresh=True)


def _publish(**_):
    from pipeline import export
    export.run()


with DAG(
    dag_id="connected_world",
    description="11 open datasets on 170 countries: land, conform, model, test, publish",
    schedule="0 6 5 * *",  # monthly
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=10)},
    tags=["open-data", "dbt", "duckdb"],
) as dag:
    extract = PythonOperator(task_id="extract_and_land_bronze", python_callable=_extract)

    dbt_build = BashOperator(
        task_id="dbt_build_models_and_tests",
        bash_command=f"cd {PROJECT / 'dbt'} && dbt build --profiles-dir .",
        env={"CONNECTED_WORLD_BRONZE": str(PROJECT / "data" / "bronze"),
             "CONNECTED_WORLD_WAREHOUSE": str(PROJECT / "data" / "warehouse.duckdb")},
        append_env=True,
    )

    publish = PythonOperator(task_id="publish_marts_and_page", python_callable=_publish)

    extract >> dbt_build >> publish
