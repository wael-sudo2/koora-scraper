# dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
import os
path = os.environ['AIRFLOW_HOME']

from datetime import timedelta, datetime

default_args = {
                'owner': 'wael',
                'depends_on_past': False,
                'email': ['wael.hkiri.dev@gmail.com'],
                'email_on_failure': True,
                'email_on_retry': False,
                'retries': 2,
                'retry_delay': timedelta(minutes=1)
                }

dag = DAG(
            dag_id='koora_dag',
            start_date=datetime(year=2025, month=3, day=30, hour=10),
            schedule_interval="0 * * * *",
            default_args=default_args,
            catchup=False
            )

task1 = BashOperator(
                        task_id='get_data',
                        bash_command=f'python {path}/dags/src/runner.py',
                        dag=dag
                    )



task1