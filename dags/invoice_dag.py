from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

log = LoggingMixin().log
log.info(f"TESSERACT_PATH visible par le DAG: {os.getenv('TESSERACT_PATH')}")


from main import batch_invoice_preprocessing

def check_path():
    log = LoggingMixin().log
    path = os.getenv('TESSERACT_PATH')
    log.info(f"TESSERACT_PATH visible par le DAG: {path}")
    print(f"[DEBUG] Tessetact_path = {path} ")
    

with DAG(
    dag_id = "lux_invoice",
    start_date=datetime(2025,1,1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    
    check_path_task = PythonOperator(
        task_id = "check_tesseract_path",
        python_callable= check_path
    )
    
    invoice_task = PythonOperator(
        task_id = "batch_invoice_preprocessing",
        python_callable=batch_invoice_preprocessing
    )
    
