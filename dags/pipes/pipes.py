import random
import time
from datetime import datetime

from airflow import DAG
from airflow.exceptions import AirflowFailException, AirflowSkipException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="Pipes",
    schedule=None,
    start_date=datetime(1970, 1, 1),
    catchup=False,
    tags=["fun"],
)


def do_something(name, do_ratio=10, skip_ratio=1, nap=1):
    """
    Do something.

    Fail or Skip or return a random number.
    """
    fate = random.choices(("fail", "skip", "do"), (1, skip_ratio, do_ratio))[0]
    time.sleep(nap)
    if fate == "fail":
        raise AirflowFailException(name)
    elif fate == "skip":
        raise AirflowSkipException(name)
    result = random.random()
    return result


def generate_pipe(name="a", m=5, do_ratio=20, skip_ratio=0, nap=0.5):
    """Generate m-nodes pipe."""

    pips = []
    for i in range(m):
        p = PythonOperator(
            task_id=f"pipa_{name}_{i}",
            python_callable=do_something,
            op_kwargs={"do_ratio": do_ratio, "skip_ratio": skip_ratio, "nap": nap},
            op_args=[f"pipa_{name}_{i}"],
            do_xcom_push=True,
        )
        if pips:
            pips[-1] >> p
        pips.append(p)
    return pips


with dag:
    start = EmptyOperator(task_id="start")
    noop = EmptyOperator(task_id="default")
    all_done_op = EmptyOperator(task_id="all_done", trigger_rule="all_done")
    always_op = EmptyOperator(task_id="always", trigger_rule="always")
    one_failed_op = EmptyOperator(task_id="one_failed", trigger_rule="one_failed")
    all_success_op = EmptyOperator(task_id="all_success", trigger_rule="all_success")
    one_success_op = EmptyOperator(task_id="one_success", trigger_rule="one_success")
    none_failed_op = EmptyOperator(task_id="none_failed", trigger_rule="none_failed")
    end = EmptyOperator(task_id="the_end", trigger_rule="all_done")
    pipe_a = generate_pipe(name="a", m=7, do_ratio=1)
    pipe_b = generate_pipe(name="b", m=5, do_ratio=10, skip_ratio=10)
    pipe_c = generate_pipe(name="c", m=3, do_ratio=100)

    group_op = [
        all_done_op,
        always_op,
        one_failed_op,
        none_failed_op,
        all_success_op,
        one_success_op,
        noop,
    ]
    for p in (pipe_a, pipe_b, pipe_c):
        start >> p[0]
        p[-1] >> group_op
    group_op >> end
