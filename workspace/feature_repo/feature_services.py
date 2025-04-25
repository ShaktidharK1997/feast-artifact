from feast import FeatureService

from features import *

# Feature service for basic prediction (v1)
flight_prediction_v1 = FeatureService(
    name="flight_prediction_v1",
    features=[
        flight_stats_fv[["Distance", "CRSElapsedTime", "DayOfWeek", "Month"]],
    ],
)

# Feature service for advanced prediction (v2)
flight_prediction_v2 = FeatureService(
    name="flight_prediction_v2",
    features=[
        flight_stats_fv,
    ],
)

# Feature service for real-time prediction with windowed features (v3)
flight_prediction_v3 = FeatureService(
    name="flight_prediction_v3",
    features=[flight_stats_fresh_fv],
)
