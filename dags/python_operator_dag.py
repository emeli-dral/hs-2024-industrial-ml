from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
	'owner':'emeli',
	'retries':2,
	'retry_delay':timedelta(minutes=2)

}

def say_hello():
	print("Hello, World! This is a Python function!")

with DAG(
	dag_id='python_dag',
	description='This is a dag to write hello world!',
	default_args=default_args,
	start_date=datetime(2024,2,16,9),
	schedule_interval='@daily',
	catchup=True

	) as dag:
		task1 = PythonOperator(
			task_id='hello',
			python_callable=say_hello
			)

		task1