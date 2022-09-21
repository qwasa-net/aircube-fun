import random
import time
from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="SleepyHeads",
    schedule="@hourly",
    start_date=datetime(1970, 1, 1),
    catchup=False,
    tags=["fun"],
)


def generate_sleepy_heads(name="a", m=5, nap_time=(1, 20)):
    """Generate m sleepy tasks."""

    def sleepy(nap):
        time.sleep(nap)
        return nap

    heads = []
    for i in range(m):
        h = PythonOperator(
            task_id=f"sleepy_head_{name}_{i}",
            python_callable=sleepy,
            op_kwargs={},
            op_args=[random.randint(*nap_time)],
            do_xcom_push=True,
        )
        heads.append(h)
    return heads


with dag:
    start = EmptyOperator(task_id="start")
    wait = EmptyOperator(task_id="wait_here")
    end = EmptyOperator(task_id="the_end")
    heads_a = generate_sleepy_heads(name="a", m=5)
    heads_b = generate_sleepy_heads(name="b", m=3)
    start >> heads_a >> wait >> heads_b >> end
