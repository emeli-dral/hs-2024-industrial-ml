from datetime import datetime, timedelta

from airflow.decorators import dag, task


default_args = {
    'owner': 'emeli',
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

@dag(dag_id='taskflow_api_dag', 
     default_args=default_args, 
     start_date=datetime(2022, 12, 12), 
     schedule_interval='@daily')

def get_data_etl():

    @task(multiple_outputs=True)
    def get_dataset_names():
        return {
            'training_dataset': 'iris_train',
            'validation_dataset': 'iris_validation'
        }

    @task()
    def get_datasource_name():
        return 'iris'

    @task()
    def print_dataset_names(source, training, validation):
        print(f'Datasource name is: {source} \n'
              f'Dataset names are: train:{training}, validation:{validation}')
    
    dataset_names = get_dataset_names()
    datasource = get_datasource_name()
    print_dataset_names(source=datasource,
        training=dataset_names['training_dataset'], 
        validation=dataset_names['validation_dataset'],
        )

get_data_tsakflow_dag = get_data_etl()