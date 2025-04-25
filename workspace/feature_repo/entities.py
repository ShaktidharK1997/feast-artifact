from feast import (
    Entity,
)


# Define an entity for the flight
flight = Entity(
    name="flight",
    join_keys=["flight_ID"],
    description="Flight identifier"
)