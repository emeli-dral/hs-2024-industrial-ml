import pandas as pd
import xgboost as xgb

from sklearn.metrics import mean_squared_error
from prefect import flow, task

xgb.set_config(verbosity=0)

@task(name='LOAD DATA', log_prints=False)
def looad_data(path):
    data = pd.read_parquet(path)
    data.lpep_dropoff_datetime = pd.to_datetime(data.lpep_dropoff_datetime)
    data.lpep_pickup_datetime = pd.to_datetime(data.lpep_pickup_datetime)

    data['duration'] = data.lpep_dropoff_datetime - data.lpep_pickup_datetime
    data.duration = data.duration.apply(lambda td: td.total_seconds() / 60)
    data = data[(data.duration >= 1) & (data.duration <= 60)]
    
    data['PULocationID'].astype(str, copy=False)
    data['DOLocationID'].astype(str, copy=False)
    return data

@task(name='GENERATE DATASET', log_prints=False)
def generate_datasets(train_frame, val_frame):
    num_features = ['trip_distance', 'extra', 'fare_amount']
    cat_features = ['PULocationID', 'DOLocationID']

    X_train = train_frame[num_features + cat_features]
    X_val = val_frame[num_features + cat_features] 

    y_train = train_frame['duration']
    y_val = val_frame['duration'] 
    return X_train, X_val, y_train, y_val

@task(name='TRAIN', retries=3, retry_delay_seconds=10, log_prints=False)
def train_model(X_train, y_train, X_val, y_val):
    best_params = {
        'max_depth':37,
        'max_leaves': 4,
        'reg_lambda': 0.11373501935624511,
        'reg_alpha': 0.036518723152379994,
        'objective': 'reg:squarederror', 
        'seed':111,

    }

    train = xgb.DMatrix(X_train, label=y_train)
    validation = xgb.DMatrix(X_val, label=y_val)

    booster = xgb.train(
        params = best_params,
        dtrain = train,
        evals = [(validation, "validation")],
        num_boost_round = 500,
        early_stopping_rounds = 50,
    )

    return booster

@task(name='QUALITY', log_prints=True)
def estimate_quality(model, X_val, y_val):
    validation = xgb.DMatrix(X_val, label=y_val)
    y_pred = model.predict(validation)
    return mean_squared_error(y_pred, y_val, squared=False)

@flow(name="DURATION FLOW")
def nyc_duration_flow():
    train_frame = looad_data('data/green_tripdata_2023-01.parquet')
    val_frame = looad_data('data/green_tripdata_2023-02.parquet')
    X_train, X_val, y_train, y_val = generate_datasets(train_frame, val_frame)

    model = train_model(X_train, y_train, X_val, y_val)
    rmse = estimate_quality(model, X_val, y_val)

if __name__=="__main__":
    nyc_duration_flow()
