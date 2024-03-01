from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
	'owner':'emeli',
	'retries':2,
	'retry_delay':timedelta(minutes=2),
}

with DAG(
	dag_id='cron_expression_dag',
	description='This is a dag to write hello world!',
	default_args=default_args,
	start_date=datetime(2022,12,1),
	schedule_interval='0 0 * * *',
	catchup=True

	) as dag:
		task1 = BashOperator(
			task_id='hello_task',
			bash_command='echo Hello, World!'
			)

		task1