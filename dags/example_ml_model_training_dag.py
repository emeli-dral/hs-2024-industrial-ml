import pandas as pd
import pickle
import csv

from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from airflow import DAG
from airflow.operators.python import PythonOperator

def dataset_preprocesssing(source_path, features_path, target_path):
	features = ['PULocationID', 'DOLocationID', 'passenger_count', 'trip_distance']
	target = 'fare_amount'

	data = pd.read_parquet(source_path)

	features_data = data[features].fillna(0)
	target_data = data[target].fillna(0)

	features_data.to_csv(features_path, index=True, sep=',')
	print(f"features succcessfully dumped to {features_path}")

	target_data.to_csv(target_path, index=True, sep=',')
	print(f"target succcessfully dumped to {target_path}")

def model_training(features_path, target_path, model_path):
	features_data = pd.read_csv(features_path, index_col=0, sep=',')
	target_data = pd.read_csv(target_path, index_col=0, sep=',')

	model = RandomForestRegressor(random_state=100)
	model.fit(features_data, target_data)

	with open(model_path, 'wb') as f_out:
		pickle.dump(model, f_out)
	print(f"model succcessfully dumped to {model_path}")

def batch_prediction_generation(model_path, features_path, preds_path):
	with open(model_path, 'rb') as f_in:
		model = pickle.load(f_in)

	features = pd.read_csv(features_path, index_col=0, sep=',')
	predictions = model.predict(features)
	pd.DataFrame(predictions).to_csv(preds_path, index=True, sep=',')
	print(f"predictions succcessfully dumped to {preds_path}")

def quality_assessment(target_path, preds_path):
	target_data = pd.read_csv(target_path, index_col=0, sep=',')
	preds_data = pd.read_csv(preds_path, index_col=0, sep=',')
	print(f"MAE: {mean_absolute_error(target_data, preds_data)}")

default_args = {
	'owner':'emeli',
	'retries':2,
	'retry_delay':timedelta(minutes=2),
}

with DAG(
	dag_id='model_training_example_dag',
	description='This is a dag with the example of model training and batch prediction!',
	default_args=default_args,
	start_date=datetime(2022,12,14,10),
	schedule_interval='@daily',

	) as dag:
		task1 = PythonOperator(
			task_id='process_train',
			python_callable=dataset_preprocesssing,
			op_kwargs={
				'source_path':'reports/green_tripdata_2021-01.parquet', 
				'features_path':'reports/train_features.csv', 
				'target_path':'reports/train_target.csv'}
			)

		task2 = PythonOperator(
			task_id='process_val',
			python_callable=dataset_preprocesssing,
			op_kwargs={
				'source_path':'reports/green_tripdata_2021-02.parquet', 
				'features_path':'reports/val_features.csv', 
				'target_path':'reports/val_target.csv'}
			)		

		task3 = PythonOperator(
			task_id='model_training',
			python_callable=model_training,
			op_kwargs={
				'model_path':'reports/trees_model.bin', 
				'features_path':'reports/val_features.csv', 
				'target_path':'reports/val_target.csv'}	
			)

		task4 = PythonOperator(
			task_id='get_train_prediction',
			python_callable=batch_prediction_generation,
			op_kwargs={
				'model_path':'reports/trees_model.bin', 
				'features_path':'reports/train_features.csv', 
				'preds_path':'reports/train_preds.csv'}	
			)

		task5 = PythonOperator(
			task_id='get_val_prediction',
			python_callable=batch_prediction_generation,
			op_kwargs={
				'model_path':'reports/trees_model.bin', 
				'features_path':'reports/val_features.csv', 
				'preds_path':'reports/val_preds.csv'}	
			)

		task6 = PythonOperator(
			task_id='score_train',
			python_callable=quality_assessment,
			op_kwargs={
				'target_path':'reports/train_target.csv', 
				'preds_path':'reports/train_preds.csv'}	
			)

		task7 = PythonOperator(
			task_id='score_val',
			python_callable=quality_assessment,
			op_kwargs={
				'target_path':'reports/val_target.csv', 
				'preds_path':'reports/val_preds.csv'}	
			)

		task1 >> task3 >> [task4, task2 >> task5]
		task5 >> task7
		task4 >> task6




