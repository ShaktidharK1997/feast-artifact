from flytekit import task, workflow
import pandas as pd
import dask.dataframe as dd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from feast import FeatureStore
import joblib
import boto3
from botocore.client import Config

@task
def load_data() -> dd.DataFrame:
    """Load flight data from MinIO using Dask"""
    storage_options = {
        'client_kwargs': {
            'endpoint_url': 'http://localhost:9000',
            'aws_access_key_id': 'minio_user',
            'aws_secret_access_key': 'minio_password',
            'region_name': 'us-east-1'
        },
        'config_kwargs': {
            'signature_version': 's3v4'
        }
    }
    
    df = dd.read_csv(
        's3://bucket/flight_performance_2024_9.csv',
        storage_options=storage_options,
        assume_missing=True
    )
    return df

@task
def prepare_features(df: dd.DataFrame) -> pd.DataFrame:
    """Transform raw data into features"""
    pdf = df.compute()
    
    # Select relevant features
    features = pdf[[
        'Month', 'DayOfWeek', 'CRSDepTime', 'CRSArrTime',
        'Distance', 'Reporting_Airline', 'Origin', 'Dest',
        'TaxiOut', 'TaxiIn', 'DepDelay', 'ArrDelay'  # Added relevant columns
    ]].copy()
    
    # Handle missing values
    features = features.fillna({
        'TaxiOut': 0,
        'TaxiIn': 0,
        'DepDelay': 0,
        'ArrDelay': 0
    })
    
    # Feature engineering
    features['CRSDepTime'] = features['CRSDepTime'].astype(str).str.zfill(4)
    features['DepHour'] = features['CRSDepTime'].str[:2].astype(int)
    features['DepMinute'] = features['CRSDepTime'].str[2:].astype(int)
    
    # Encode categorical variables
    le = LabelEncoder()
    for col in ['Reporting_Airline', 'Origin', 'Dest']:
        features[col + '_encoded'] = le.fit_transform(features[col])
    
    # Create route feature
    features['Route'] = features['Origin'] + '_' + features['Dest']
    
    return features

@task
def train_model(features: pd.DataFrame) -> str:
    """Train Random Forest model with optimized parameters for 8GB RAM"""
    # Prepare features for training
    feature_cols = [
        'Month', 'DayOfWeek', 'DepHour', 'DepMinute',
        'Distance', 'TaxiOut', 'TaxiIn',
        'Reporting_Airline_encoded', 'Origin_encoded', 'Dest_encoded'
    ]
    
    X = features[feature_cols]
    y = features['ArrDelay']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Initialize model with memory-conscious parameters
    model = RandomForestRegressor(
        n_estimators=50,  # Reduced for memory constraints
        max_depth=8,      # Limited depth
        min_samples_split=10,
        min_samples_leaf=4,
        n_jobs=2,         # Limited parallel jobs
        random_state=42
    )
    
    # Train model
    model.fit(X_train, y_train)
    
    # Calculate and print metrics
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Train R2 Score: {train_score:.4f}")
    print(f"Test R2 Score: {test_score:.4f}")
    
    # Save model
    model_path = '/tmp/flight_delay_model.joblib'
    joblib.dump(model, model_path)
    
    return model_path

@task
def register_features(features: pd.DataFrame):
    """Register features with Feast"""
    store = FeatureStore(repo_path="feature_repo")
    
    # Create entity DataFrame with timestamps
    entity_df = pd.DataFrame({
        'Origin': features['Origin'],
        'Dest': features['Dest'],
        'FlightDate': pd.to_datetime(features['FlightDate'])
    })
    
    # Get features from store
    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=[
            'flight_performance:month',
            'flight_performance:day_of_week',
            'flight_performance:distance',
            'flight_performance:carrier_code',
            'flight_performance:dep_delay',
            'flight_performance:taxi_out',
            'flight_performance:taxi_in',
        ],
    ).to_df()
    
    return training_df

@workflow
def flight_delay_prediction_pipeline() -> str:
    """Main workflow for flight delay prediction"""
    # Load data
    raw_data = load_data()
    
    # Prepare features
    features = prepare_features(raw_data)
    
    # Register features with Feast
    registered_features = register_features(features)
    
    # Train model
    model_path = train_model(registered_features)
    
    return model_path
