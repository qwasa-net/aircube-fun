"""
Acca.

One DAG, multiple tasks, one results collector, XCOM is used to pass results between DAGs.
"""
import logging
import random
from datetime import datetime

from airflow import DAG
from airflow.exceptions import AirflowFailException, AirflowSkipException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

dag = DAG(
    dag_id="Acca",
    schedule="@hourly",
    start_date=datetime(1970, 1, 1),
    catchup=False,
    tags=["fun"],
)


def do_something(name):
    """
    Do something.

    Fail or Skip or return a random number.
    """
    fate = random.choices(("fail", "skip", "do"), (1, 1, 15))[0]
    if fate == "fail":
        raise AirflowFailException(name)
    elif fate == "skip":
        raise AirflowSkipException(name)
    result = random.random()
    return result


def create_noop_tasks_layer(name, m):
    """Generate m NoopOperators."""
    ops_layer = []
    task_ids = []
    for i in range(m):
        task_id = f"noop_{name}_{i}"
        task_ids.append(task_id)
        h = PythonOperator(
            task_id=task_id,
            python_callable=do_something,
            op_kwargs={},
            op_args=[task_id],
            do_xcom_push=True,
        )
        ops_layer.append(h)
    return ops_layer, task_ids


def do_calculate(task_ids, **kwargs):
    """Calculate the sum of the results of the tasks."""
    ti = kwargs["ti"]
    values = ti.xcom_pull(task_ids=task_ids, key="return_value")
    result = sum(values)
    logging.info("task_ids=%s", task_ids)
    logging.info("values=%s", values)
    logging.info("count(values)=%s", len(values))
    logging.info("sum=%s", result)
    return result


def create_acca_task(task_ids):
    """Create a task that collects results of the tasks."""
    op = PythonOperator(
        task_id="acca",
        python_callable=do_calculate,
        op_args=[task_ids],
        do_xcom_push=True,
        trigger_rule=TriggerRule.ALL_DONE,
    )
    return op


# do the do right here
with dag:

    # task [START]
    start = EmptyOperator(task_id="start")

    # tasks martix [NOOP]
    layers = []
    noop_task_ids = []
    depth, scale = 4, 2
    for i in range(depth):
        ops, tids = create_noop_tasks_layer(f"{i}", scale ** (i + 1))
        layers.append(ops)
        noop_task_ids += tids

    # task [ACCA]
    acca = create_acca_task(noop_task_ids)

    # task [END]
    end = EmptyOperator(task_id="the_end", trigger_rule=TriggerRule.ALL_DONE)

    # build task deps
    start >> layers[0]

    for i in range(1, len(layers)):
        parent = layers[i - 1]
        current = layers[i]
        for j in range(len(parent)):
            parent[j] >> current[j * scale : (j + 1) * scale]

    layers[-1] >> acca >> end

# I was here
logging.warning("this is %s %s", __file__)
