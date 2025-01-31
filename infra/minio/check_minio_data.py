import boto3
from botocore.client import Config

def create_minio_client(endpoint_url, access_key, secret_key, secure=False):
    """
    Create an S3 client configured to interact with MinIO
    
    Args:
        endpoint_url (str): MinIO server endpoint URL
        access_key (str): Access key for authentication
        secret_key (str): Secret key for authentication
        secure (bool): Use HTTPS if True, HTTP if False
    
    Returns:
        boto3.client: Configured S3 client
    """
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        verify=secure
    )

def list_buckets(s3_client):
    """List all buckets in the MinIO instance"""
    response = s3_client.list_buckets()
    for bucket in response['Buckets']:
        print(f"Bucket: {bucket['Name']}")

def list_objects(s3_client, bucket_name, prefix=''):
    """
    List objects in a specific bucket
    
    Args:
        s3_client: boto3 S3 client
        bucket_name (str): Name of the bucket
        prefix (str): Optional prefix to filter objects
    """
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                print(f"Object: {obj['Key']}, Size: {obj['Size']} bytes")

def get_object_metadata(s3_client, bucket_name, object_key):
    """
    Get metadata for a specific object
    
    Args:
        s3_client: boto3 S3 client
        bucket_name (str): Name of the bucket
        object_key (str): Key of the object
    """
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        print(f"Metadata for {object_key}:")
        print(f"Content Type: {response.get('ContentType')}")
        print(f"Last Modified: {response.get('LastModified')}")
        print(f"Content Length: {response.get('ContentLength')} bytes")
        print(f"ETag: {response.get('ETag')}")
        if 'Metadata' in response:
            print("Custom Metadata:")
            for key, value in response['Metadata'].items():
                print(f"  {key}: {value}")
    except s3_client.exceptions.ClientError as e:
        print(f"Error getting metadata: {e}")

# Example usage:
if __name__ == "__main__":
    # Configure these variables according to your MinIO setup
    MINIO_ENDPOINT = "http://localhost:9000"
    ACCESS_KEY = "minio_user"
    SECRET_KEY = "minio_password"
    
    # Create S3 client
    s3_client = create_minio_client(MINIO_ENDPOINT, ACCESS_KEY, SECRET_KEY)
    
    # List all buckets
    print("Listing all buckets:")
    list_buckets(s3_client)
    
    # Example: List objects in a specific bucket
    BUCKET_NAME = "bucket"
    print(f"\nListing objects in bucket '{BUCKET_NAME}':")
    list_objects(s3_client, BUCKET_NAME)
