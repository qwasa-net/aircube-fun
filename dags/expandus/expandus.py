"""
Expandus.

"""
import logging
import random
from datetime import datetime
from airflow.decorators import task, dag

from airflow import DAG
from airflow.operators.empty import EmptyOperator

dag = DAG(
    dag_id="Expandus",
    schedule=None,
    start_date=datetime(1970, 1, 1),
    catchup=False,
    tags=["fun"],
)


# do the do right here
with dag:

    @task
    def do_n1(n: int = 3, ab: tuple = (0, 100)):
        return [random.randint(*ab) for _ in range(random.randint(n, 2 * n))]

    @task
    def do_n2(value, m: int = 5):
        return [value] * m

    @task
    def summer(values):
        flat = [v for vv in values for v in vv]
        return sum(flat), len(flat)

    # END
    end = EmptyOperator(task_id="end")

    group = summer(
        values=do_n2.partial(m=7).expand(
            value=do_n1(n=5),
        ),
    )

    [group] >> end

# I was here
logging.warning("this is %s", __file__)
