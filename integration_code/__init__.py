import os
from dask.distributed import Client

# Global client variable
client = None

def get_dask_client():
    """Get the global Dask client instance."""
    return client

def init_dask():
    """Initialize Dask client with connection to scheduler."""
    global client
    
    # Connect to the Dask scheduler
    client = Client('localhost:8786')
    
    # Print cluster information for verification
    print(f"Dask Dashboard URL: {client.dashboard_link}")
    print(f"Connected to Dask cluster with {len(client.scheduler_info()['workers'])} workers")
    
    return client

def close_dask():
    """Properly close Dask client connection."""
    global client
    if client is not None:
        client.close()
        client = None

def get_registry_path():
    """Get the registry path from environment variable."""
    return os.environ["REGISTRY_PATH"]

def get_feature_folder_path():
    """Get the feature folder path from environment variable."""
    return os.environ["FEATURE_FOLDER_PATH"]

# Initialize Dask client when module is imported
init_dask()

# Ensure proper cleanup on program exit
import atexit
atexit.register(close_dask)
