from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
	'owner':'emeli',
	'retries':2,
	'retry_delay':timedelta(minutes=2)

}

with DAG(
	dag_id='bash_dag',
	description='This is a dag to write hello world!',
	default_args=default_args,
	start_date=datetime(2024,2,29,9),
	schedule_interval='@daily',

	) as dag:
		task1 = BashOperator(
			task_id='first_task',
			bash_command='echo Hello, World!'
			)

		task1 
