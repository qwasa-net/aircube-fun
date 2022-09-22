"""
Deus.

Multiple DAGs with simple pipe of tasks.
"""

import logging
import time
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule


def create_dag(dag_id: str, n: int):
    """Create a DAG with n piped tasks."""
    dag = DAG(
        dag_id=dag_id,
        schedule=None,
        start_date=datetime(1970, 1, 1),
        catchup=False,
        tags=["fun"],
    )
    tasks = []
    for i in range(n):
        task_id = f"{dag_id}_t{i+1:02}"
        task = create_dag_task(dag, task_id)
        if tasks:
            tasks[-1] >> task
        tasks.append(task)

    return dag


def do_nothing(name):
    """Do nothing."""
    logging.info("start: %s", name)
    time.sleep(1)
    logging.info("finish: %s", name)


def create_dag_task(dag, task_id):
    """Create a NOOP task."""
    op = PythonOperator(
        dag=dag,
        task_id=task_id,
        python_callable=do_nothing,
        op_args=[task_id],
        do_xcom_push=True,
        trigger_rule=TriggerRule.ALL_DONE,
    )
    return op


def generate_many_dags(m: int, n: int) -> dict:
    """Generate m DAGs with n piped tasks."""
    dags = {}
    for i in range(m):
        dag_id = f"deus_x{i+1:02}"
        dag = create_dag(dag_id, n)
        global_var_name = f"dag_{dag_id}"
        dags[global_var_name] = dag
    return dags


# do the do and generate the DAGs
dags = generate_many_dags(8, 10)

# add generated DAGs to the globals
globals().update(dags)

# I was here
logging.warning("this is %s %s", __file__, globals().keys())
