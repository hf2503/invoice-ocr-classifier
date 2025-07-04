from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import convert_invoice_pdf



with DAG(
    dag_id = "lux_invoice",
    start_date=datetime(2025,1,1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id = "convert_invoice_pdf",
        python_callable= convert_invoice_pdf
    )
