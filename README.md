# Flight Delay Prediction using Feast Feature Store

This repository demonstrates how to use Feast feature store for managing features in a flight delay prediction system. The tutorial covers setting up a feature store, defining feature views, and working with both historical and online features.

## Project Structure

```
feast-artifact/
├── feature_repo/
│   ├── data/
│   │   └── flights.parquet
│   ├── Feast.ipynb
│   ├── feature_definition.py
│   └── feature_store.yaml
├── .github/
│   └── workflows/
└── integration_code(not_ready)/
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ShaktidharK1997/feast-artifact.git
cd feast-artifact
```

### 2. Set Up Python Environment

Install required packages for Python environment

```bash
pip install -r requirements.txt
```

### 3. Initialize Feast Feature Store

Navigate to the feature repository directory:

```bash
cd feature_repo
feast apply
```

This command will:
- Register your feature definitions
- Create necessary infrastructure
- Set up the online store

### 4. Run the Tutorial

Open and run the Jupyter notebook:

```bash
jupyter notebook Feast.ipynb
```

The notebook contains:
- Feature store initialization
- Historical feature retrieval examples
- Online feature serving examples
- Real-time feature updates demonstration

### 5. Clean Up

After completing the tutorial, clean up the feature store:

```bash
feast teardown
```

This will remove all feature store infrastructure created during the tutorial.

## Tutorial Contents

1. **Feature Definitions**: Understanding how to define entities, feature views, and feature services
2. **Historical Features**: Working with point-in-time correct feature retrieval
3. **Online Features**: Real-time feature serving capabilities
4. **Feature Store Operations**: Materialization and feature updates
5. **Real-time Updates**: Simulating streaming data updates

