from datetime import timedelta
from feast import (
    FeatureView,
    Field,
)

from feast.types import Float32, Float64, Int64, String, Bool

from data_sources import *
from entities import *


# Define the main feature view with File Source
# This feature view will be used for batch processing and historical analysis
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
        # New holiday features
        Field(name="is_holiday", dtype=Int64),
        Field(name="days_to_nearest_holiday", dtype=Int64),
        # New route-based features
        Field(name="Route", dtype=String),
        Field(name="route_avg_delay_24h", dtype=Float32),
        Field(name="route_max_delay_24h", dtype=Float32),
    ],
    online=True,
    source=flight_stats_source,
    tags={"team": "flight_ops"},
)


# Feature view for real-time flight stats
# This feature view will be used for real-time predictions and online serving
# It uses a push source to get real-time updates
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
        # New holiday features
        Field(name="is_holiday", dtype=Int64),
        Field(name="days_to_nearest_holiday", dtype=Int64),
        # New route-based features
        Field(name="Route", dtype=String),
        Field(name="route_avg_delay_24h", dtype=Float32),
        Field(name="route_max_delay_24h", dtype=Float32),
    ],
    online=True,
    source=flight_stats_push_source,
    tags={"team": "flight_ops"},
)


