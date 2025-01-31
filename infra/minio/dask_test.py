from dask.distributed import Client

# Connect to Dask
client = Client('tcp://localhost:8786')

# Create some test data
import dask.array as da
array = da.random.random((10000, 10000))

# Run a computation
result = array.mean().compute()
print(f"Computation result: {result}")

# Check worker status
print("\nCluster Status:")
print(client.scheduler_info()['workers'])