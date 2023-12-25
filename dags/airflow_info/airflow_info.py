import pkgutil
import sys
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.operators.empty import EmptyOperator

HUGE_SIZE = 64 * 1024 * 1024


@dag(
    dag_id="show-airflow-info",
    schedule="5/15 * * * *",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    dagrun_timeout=timedelta(hours=1),
    start_date=datetime(2022, 9, 28),
    tags=["test"],
    default_args={},
)
def show_airflow_info(**kwargs):
    @task(task_id="show-airflow-info")
    def get_info(**kwargs):
        # python version
        print("sys.version=", sys.version)
        # installed modules
        for module in pkgutil.iter_modules():
            print(module.name, module.module_finder)

    @task(task_id="burn-it")
    def burn_it(i, **kwargs):
        a = "a"
        astring = a * HUGE_SIZE
        for c in astring:
            if c != a:
                raise AirflowFailException("burned")

    start = EmptyOperator(task_id="start")
    info_operator = get_info()
    burn_operator = burn_it.expand(i=[1, 2, 3, 4])
    end = EmptyOperator(task_id="end")

    start >> info_operator >> end
    burn_operator >> end


dag_show_airflow_info = show_airflow_info()
