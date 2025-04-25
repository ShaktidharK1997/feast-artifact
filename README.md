# Flight Delay Prediction with Feast Feature Store

This repository demonstrates how to use Feast feature store for managing ML features in a flight delay prediction system. It shows how to set up a feature repository, define entities and feature views, and work with both historical and real-time features.

## Quick Start

### 1. Start the Jupyter Notebook 

Launch the Docker containers for Jupyter in the SSH terminal : 

```bash
docker-compose -f /home/cc/feast-artifact/docker/docker-compose-feast.yml jupyter up -d
```

### 2. Access Jupyter Notebook

Check the Jupyter server logs to get the access URL:

```bash
docker logs jupyter
```

Look for a URL that looks like `http://127.0.0.1:8888/?token=...` in the output and open it in your browser.

### 3. Follow the Tutorial

Navigate to `/work/workspace/feast_tutorial.ipynb` in the Jupyter interface and follow along with the tutorial. The notebook includes:

- Setting up a Feast feature repository
- bringing up Feast infrastructure
- Defining entities and feature views
- Retrieving historical features for model training
- Serving real-time features for prediction
- Implementing a streaming pipeline for feature updates

## Repository Structure

- `workspace/feature_repo/`: Contains Feast configuration and feature definitions
  - `data_sources.py`: Defines data sources (file, push)
  - `entities.py`: Defines the flight entity
  - `features.py`: Defines feature views
  - `feature_services.py`: Groups features for different models
  - `feature_store.yaml`: Main configuration file

- `workspace/feast_tutorial.ipynb`: Step-by-step tutorial notebook
- `dags/`: Airflow DAGs for scheduled feature materialization
- `docker/`: Docker Compose configurations

## Cleanup

When finished, stop all services:

```bash
docker-compose -f /home/cc/feast-artifact/docker/docker-compose-feast.yml down
docker-compose -f /home/cc/feast-artifact/docker/docker-compose-airflow.yml down
```
