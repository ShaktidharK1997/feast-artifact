from datetime import timedelta
import pandas as pd
from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    FileSource,
    PushSource,
    Project,
    RequestSource,
)
#from feast.infra.offline_stores.file_source import FileSource

from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int64, String
from feast.data_format import ParquetFormat

import s3fs

# Define a project for the feature repo
project = Project(
    name="flight_delay_project",
    description="A project for flight delay prediction"
)

# Define an entity for the flight
flight = Entity(
    name="flight",
    join_keys=["flight_ID"],
    description="Flight identifier"
)

bucket_name = "feast-bucket"
file_name = "flights.parquet"
s3_endpoint = "https://localhost:9000" 


# Define the data source for flight data
flight_stats_source = FileSource(
    path=f"s3://{bucket_name}/{file_name}",  
    timestamp_field="FlightDate",
    file_format=ParquetFormat(),
    s3_endpoint_override="http://localhost:9000"  # Changed to http since use_ssl=False
)

# Define the main feature view
flight_stats_fv = FeatureView(
    name="flight_stats",
    entities=[flight],
    ttl=timedelta(days=30),
    schema=[
        # Basic flight information
        Field(name="Origin", dtype=String),
        Field(name="Dest", dtype=String),
        Field(name="Distance", dtype=Float32),
        Field(name="CRSElapsedTime", dtype=Float32),
        # Time-based features
        Field(name="DayOfWeek", dtype=Int64),
        Field(name="Month", dtype=Int64),
        Field(name="Quarter", dtype=Int64),
        # Delay features
        Field(name="DepDelay", dtype=Float32),
        Field(name="CarrierDelay", dtype=Float32),
        Field(name="WeatherDelay", dtype=Float32),
        Field(name="NASDelay", dtype=Float32),
        Field(name="SecurityDelay", dtype=Float32),
        Field(name="LateAircraftDelay", dtype=Float32),
        # Target variable
        Field(name="ArrDelay", dtype=Float32),
    ],
    online=True,
    source=flight_stats_source,
    tags={"team": "flight_ops"},
)

# Define a request data source for real-time features
input_request = RequestSource(
    name="real_time_features",
    schema=[
        Field(name="weather_severity", dtype=Int64),
        Field(name="airport_congestion", dtype=Int64),
    ],
)

# Define an on-demand feature view for real-time delay predictions
@on_demand_feature_view(
    sources=[flight_stats_fv, input_request],
    schema=[
        Field(name="predicted_delay_weather", dtype=Float64),
        Field(name="predicted_delay_congestion", dtype=Float64),
    ],
)
def transformed_delay_prediction(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    # Combine historical weather delays with current weather severity
    df["predicted_delay_weather"] = inputs["WeatherDelay"] * (inputs["weather_severity"] / 100)
    # Combine historical NAS delays with current airport congestion
    df["predicted_delay_congestion"] = inputs["NASDelay"] * (inputs["airport_congestion"] / 100)
    return df

# Feature service for basic prediction (v1)
flight_prediction_v1 = FeatureService(
    name="flight_prediction_v1",
    features=[
        flight_stats_fv[["Distance", "CRSElapsedTime", "DayOfWeek", "Month"]],
      #  transformed_delay_prediction,
    ],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)

# Feature service for advanced prediction (v2)
flight_prediction_v2 = FeatureService(
    name="flight_prediction_v2",
    features=[
        flight_stats_fv,
     #   transformed_delay_prediction,
    ],
)

# Define push source for real-time updates
flight_stats_push_source = PushSource(
    name="flight_stats_push_source",
    batch_source=flight_stats_source,
)

# Feature view for real-time flight stats
flight_stats_fresh_fv = FeatureView(
    name="flight_stats_fresh",
    entities=[flight],
    ttl=timedelta(days=30),
    schema=[
        Field(name="Origin", dtype=String),
        Field(name="Dest", dtype=String),
        Field(name="Distance", dtype=Float32),
        Field(name="CRSElapsedTime", dtype=Float32),
        Field(name="DayOfWeek", dtype=Int64),
        Field(name="Month", dtype=Int64),
        Field(name="Quarter", dtype=Int64),
        Field(name="DepDelay", dtype=Float32),
        Field(name="WeatherDelay", dtype=Float32),
        Field(name="NASDelay", dtype=Float32),
    ],
    online=True,
    source=flight_stats_push_source,
    tags={"team": "flight_ops"},
)

# On-demand feature view for real-time predictions using fresh data

@on_demand_feature_view(
    sources=[flight_stats_fresh_fv, input_request],
    schema=[
        Field(name="predicted_delay_weather", dtype=Float64),
        Field(name="predicted_delay_congestion", dtype=Float64),
    ],
)
def transformed_delay_prediction_fresh(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["predicted_delay_weather"] = inputs["WeatherDelay"] * (inputs["weather_severity"] / 100)
    df["predicted_delay_congestion"] = inputs["NASDelay"] * (inputs["airport_congestion"] / 100)
    return df

# Feature service for real-time prediction (v3)
flight_prediction_v3 = FeatureService(
    name="flight_prediction_v3",
    features=[flight_stats_fresh_fv],
)
