import os
from feast import (
    FileSource,
    PushSource,
)

from feast.data_format import ParquetFormat

# Data sources 

# File Source 
"""
flight_stats_source = FileSource(
    path=f"data/flights_v1.parquet",
    timestamp_field="FlightDate",
    file_format=ParquetFormat()
)

"""

bucket_name = "feast"
file_name = "flights_v1.parquet"


# Define the data source for flight data
flight_stats_source = FileSource(
    path=f"s3://{bucket_name}/{file_name}",  
    timestamp_field="FlightDate",
    file_format=ParquetFormat(),
    s3_endpoint_override="http://minio:9000"  # Changed to http since use_ssl=False
)


# Push source for real-time updates
flight_stats_push_source = PushSource(
    name="flight_stats_push_source",
    batch_source=flight_stats_source,
)
