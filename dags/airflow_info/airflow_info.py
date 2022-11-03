import pkgutil
import sys
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator


@dag(
    dag_id="show-airflow-info",
    schedule=None,
    catchup=False,
    start_date=datetime(1970, 1, 1),
    tags=["test"],
    default_args={},
)
def show_airflow_info(**kwargs):
    @task(task_id="show_airflow_info")
    def get_info(**kwargs):
        print(f"{sys.version=}")
        print(f"{sys.path=}")
        for module in pkgutil.iter_modules():
            print(module.name, module.module_finder)

    start = EmptyOperator(task_id="start")
    info_operator = get_info()
    end = EmptyOperator(task_id="end")

    start >> info_operator >> end


dag_show_airflow_info = show_airflow_info()
