import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from botocore.client import Config
import os

# MinIO (or S3) connection details
minio_host = "localhost:9000"  
access_key = "minio_user"      
secret_key = "minio_password"  
bucket_name = "feast-bucket"         

# Initialize the S3 client with proper MinIO configuration
s3_client = boto3.client(
    's3',
    endpoint_url=f'http://{minio_host}',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    aws_session_token=None,
    config=Config(signature_version='s3v4'),
    verify=False,  # Required for self-signed certificates
    region_name='us-east-1'
)

# Suppress warnings about unverified HTTPS requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    s3_client.head_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' exists.")
except Exception as e:
    print(f"Bucket '{bucket_name}' does not exist. Creating it now...")
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    except Exception as e:
        print(f"Error creating bucket: {e}")

file_path = "data/flights.parquet"
object_name = "flights.parquet"
print(file_path)
if not os.path.isfile(file_path):
    print(f"File '{file_path}' does not exist!")
    exit(1)

try:
    s3_client.upload_file(file_path, bucket_name, object_name)
    print(f"File '{file_path}' uploaded successfully to '{bucket_name}/{object_name}'.")
except (NoCredentialsError, PartialCredentialsError):
    print("Invalid credentials. Please check your access key and secret key.")
except Exception as e:
    print(f"Error uploading file: {e}")
