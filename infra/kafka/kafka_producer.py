import json
from time import sleep

import pandas as pd
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
import argparse

parser = argparse.ArgumentParser(description='Argument parsing for Kafka Producer')
parser.add_argument("-m",
                    "--mode", 
                    default="setup",
                    choices=["setup", "teardown"],
                    required=False, 
                    type=str,
                    help="Argument specifies whether to setup or teardown Kafka topic with flight events. Setup will teardown before beginning emitting events")

parser.add_argument("-b",
                    "--bootstrap_servers",
                    default="localhost:9092",
                    help="Where the bootstrap server is"
                    )

args = parser.parse_args()

def create_stream(topic_name, servers):
    
    producer = None
    admin = None

    producer = None
    admin = None
    for i in range(20):
        try:
            producer = KafkaProducer(bootstrap_servers=servers)
            admin = KafkaAdminClient(bootstrap_servers=servers)
            print("SUCCESS: instantiated Kafka admin and producer")
            break
        except Exception as e:
            print(
                f"Trying to instantiate admin and producer with bootstrap servers {servers} with error {e}"
            )
            sleep(10)
            pass

    try:
        # Create Kafka topic
        topic = NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
        admin.create_topics([topic])
        print(f"Topic {topic_name} created")
    except Exception as e:
        print(str(e))
        pass

    print("Reading parquet")
    df = pd.read_parquet("flights.parquet")
    print("Emitting events")

    # Function to simulate fresher data by updating timestamps
    def update_timestamps(row, iteration):
        # Convert FlightDate to datetime
        flight_date = pd.to_datetime(row["FlightDate"])
        # Add weeks to simulate fresher data
        updated_flight_date = flight_date + pd.Timedelta(weeks=52 * iteration)
        row["FlightDate"] = updated_flight_date.strftime("%Y-%m-%d")
        return row

    iteration = 1
    while True:
        for row in df[
            ["Year", "Quarter", "Month", "DayofMonth", "DayOfWeek", "FlightDate", 
            "CRSDepTime", "CRSArrTime", "DepTime", "ArrTime", "Reporting_Airline", 
            "Origin", "Dest", "Distance"]
        ].to_dict("records"):
            # Update timestamps to simulate fresher data
            row = update_timestamps(row, iteration)
            # Send the row to Kafka
            producer.send(topic_name, json.dumps(row).encode())
            sleep(0.1) 
        iteration += 1

def teardown_stream(topic_name, servers=["localhost:9092"]):
    try:
        admin = KafkaAdminClient(bootstrap_servers=servers)
        print(admin.delete_topics([topic_name]))
        print(f"Topic {topic_name} deleted")
    except Exception as e:
        print(str(e))
        pass

if __name__ == "__main__":
    parsed_args = vars(args)
    mode = parsed_args["mode"]
    servers = parsed_args["bootstrap_servers"]
    teardown_stream("drivers", [servers])
    if mode == "setup":
        create_stream("drivers", [servers])