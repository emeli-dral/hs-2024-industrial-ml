from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
	'owner':'emeli',
	'retries':2,
	'retry_delay':timedelta(minutes=2)

}

def pandas_pandas_version():
	import pandas as pd
	print(f"pandas version: {pd.__version__}")

with DAG(
	dag_id='python_external_library_dag',
	description='This dag uses pandas library!',
	default_args=default_args,
	start_date=datetime(2022,12,12),
	schedule_interval='@daily',

	) as dag:
		task1 = PythonOperator(
			task_id='print_pandas_version',
			python_callable=pandas_pandas_version
			)

		task1