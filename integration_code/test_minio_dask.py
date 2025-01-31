
import time
import logging
from datetime import datetime
import boto3
import botocore
import dask.distributed
from botocore.client import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dask_cluster(scheduler_address="tcp://localhost:8786", timeout=30):
    """
    Check if Dask cluster is operational by connecting to scheduler and verifying workers.
    """
    try:
        logger.info(f"Attempting to connect to Dask scheduler at {scheduler_address}")
        client = dask.distributed.Client(scheduler_address, timeout=timeout)
        
        # Wait for workers to connect
        start_time = time.time()
        while len(client.scheduler_info()['workers']) == 0:
            if time.time() - start_time > timeout:
                raise TimeoutError("No workers connected within timeout period")
            time.sleep(1)
            
        worker_count = len(client.scheduler_info()['workers'])
        logger.info(f"Successfully connected to Dask cluster with {worker_count} workers")
        
        # Run a simple computation to verify cluster is working
        future = client.submit(lambda x: x + 1, 10)
        result = future.result(timeout=timeout)
        logger.info("Successfully ran test computation on Dask cluster")
        
        return True, {
            'worker_count': worker_count,
            'scheduler_address': scheduler_address
        }
        
    except Exception as e:
        logger.error(f"Failed to connect to Dask cluster: {str(e)}")
        return False, str(e)
    finally:
        try:
            client.close()
        except:
            pass

def check_s3(endpoint_url="http://localhost:9000", 
             access_key = "minio_user",
             secret_key = "minio_password",
             test_bucket="test-bucket"):
    """
    Check if S3 storage is operational using boto3.
    """
    try:
        logger.info(f"Attempting to connect to S3 at {endpoint_url}")
        
        # Create S3 client with custom endpoint
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
	    region_name = 'us-east-1',	
        )
        
        # Check if test bucket exists, create if it doesn't
        try:
            s3_client.head_bucket(Bucket=test_bucket)
        except botocore.exceptions.ClientError:
            logger.info(f"Creating test bucket: {test_bucket}")
            s3_client.create_bucket(Bucket=test_bucket)
        
        # Write test file
        test_data = f"Test data {datetime.now().isoformat()}"
        test_file = "test.txt"
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_file,
            Body=test_data
        )
        logger.info("Successfully wrote test file to S3")
        
        # Read test file
        response = s3_client.get_object(
            Bucket=test_bucket,
            Key=test_file
        )
        data = response['Body'].read().decode('utf-8')
        logger.info("Successfully read test file from S3")
        
        # Clean up
        s3_client.delete_object(
            Bucket=test_bucket,
            Key=test_file
        )
        s3_client.delete_bucket(Bucket=test_bucket)
        logger.info("Successfully cleaned up test bucket and file")
        
        # List remaining buckets
        buckets = s3_client.list_buckets()['Buckets']
        
        return True, {
            'endpoint': endpoint_url,
            'buckets': [bucket['Name'] for bucket in buckets]
        }
        
    except botocore.exceptions.ClientError as e:
        logger.error(f"S3 client error: {str(e)}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Failed to connect to S3: {str(e)}")
        return False, str(e)

def main():

    # Check S3
    s3_success, s3_info = check_s3()
    if s3_success:
        logger.info("✅ S3 storage is operational")
        logger.info(f"S3 info: {s3_info}")
    else:
        logger.error("❌ S3 check failed")
        logger.error(f"Error: {s3_info}")

    # Check Dask
    dask_success, dask_info = check_dask_cluster()
    if dask_success:
        logger.info("✅ Dask cluster is operational")
        logger.info(f"Dask info: {dask_info}")
    else:
        logger.error("❌ Dask cluster check failed")
        logger.error(f"Error: {dask_info}")

    # Overall status
    if dask_success and s3_success:
        logger.info("🚀 All systems operational!")
        return 0
    else:
        logger.error("⚠️ Some checks failed")
        return 1

if __name__ == "__main__":
    exit(main())
