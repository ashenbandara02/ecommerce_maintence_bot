import boto3
from botocore.client import Config
from boto3.s3.transfer import TransferConfig, S3Transfer
from tqdm import tqdm
import threading
import os

# Define your R2 credentials and configuration
account_id = "877dbcf9dea9f7ba000a54bb27a266a9"
access_key_id = "d159bbe88e5a76a885a837659d3afcc9"
secret_access_key = "94f438793c5388c500b623e54ad2d52bc914086224c8a4a8e979f3996a00fbd7"
bucket_name = "storage-wptoolmart"

# Configure the S3 client for Cloudflare R2
s3_client = boto3.client(
    's3',
    endpoint_url=f'https://877dbcf9dea9f7ba000a54bb27a266a9.r2.cloudflarestorage.com',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            print(f"\r{self._filename}  {percentage:.2f}% completed", end="")
        
        return "Complete"

# Set up transfer config
config = TransferConfig(multipart_threshold=8 * 1024 * 1024)  # 8 MB threshold for multipart
transfer = S3Transfer(s3_client, config)

def list_bucket_items():
    """Retrieve all items from the bucket."""
    items = []
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        if 'Contents' in page:
            items.extend([item['Key'] for item in page['Contents']])
    return items

def check_if_file_exists(link):
    """Check if a file exists in the bucket."""
    items = list_bucket_items()
    return link in items


def delete_file(file_name):
    """Delete a file from the bucket."""
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        print(f"\nFile '{file_name}' deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting file '{file_name}': {e}")
        return False
    

# Uploads the file and generate the static link and returns success/Wrong if success returns the static link of the file
# args are file 
def upload_static_action(file, file_name):
    upload_status = transfer.upload_file(file, bucket_name, file_name, callback=ProgressPercentage(file))
    public_url = f"https://storage.wptoolmart.com/{file_name}"
    return public_url

# print(delete_file("IT24100315.jpg"))
# Download the file from the R2 bucket
# s3_client.download_file(bucket_name, object_key, download_file_path)
# print(f'Downloaded {bucket_name}/{object_key} to {download_file_path}')
# print(upload_static_action("done.txt", "done.txt"))
# sampple
# https://pub-ec0b5baa55bc467f8e9fe202656da58e.r2.dev/Accare-HeatingAirConditioning-12-00010524-3dtoux-zzjcxz-RnZkM1a70z-QfAC0c1SJR.zip