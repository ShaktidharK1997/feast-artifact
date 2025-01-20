from dask.distributed import Client
import time
import socket

def wait_for_scheduler():
    print("Checking scheduler connectivity...")
    retries = 30
    for i in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('scheduler', 8786))
            sock.close()
            
            if result == 0:
                print("✓ Scheduler port is open!")
                return True
        except Exception as e:
            print(f"Attempt {i+1}: {str(e)}")
        
        print(f"Attempt {i+1}: Waiting for scheduler...")
        time.sleep(1)
    return False

def main():
    print("Starting Dask connection test...")
    
    if not wait_for_scheduler():
        print("Failed to connect to scheduler after retries")
        return
    
    try:
        print("\nConnecting to Dask cluster...")
        client = Client("tcp://scheduler:8786")
        print("✓ Successfully connected to Dask cluster!")
        print(f"Dashboard link: {client.dashboard_link}")
        
        # Test computation
        print("\nTesting computation...")
        future = client.submit(lambda x: x + 1, 10)
        result = future.result(timeout=5)
        print(f"✓ Test computation result: {result}")
        
        # Get cluster info
        print("\nCluster information:")
        info = client.scheduler_info()
        print(f"Workers: {len(info['workers'])}")
        print(f"Total threads: {info['workers'][list(info['workers'].keys())[0]]['nthreads']}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    print("Waiting for services to start...")
    time.sleep(5)
    main()
