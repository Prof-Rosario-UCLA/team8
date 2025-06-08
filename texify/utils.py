import os
from google.cloud import storage
from google.cloud.storage.client import Client
from google.auth.credentials import AnonymousCredentials
from dotenv import load_dotenv

load_dotenv()

USE_EMULATOR = os.getenv("GCS_EMULATOR") == "1"
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def get_storage_client() -> Client:
    if USE_EMULATOR:
        return storage.Client(
            credentials=AnonymousCredentials(),
            project="test-project",
            client_options={"api_endpoint": os.getenv("GCS_EMULATOR_HOST")},
        )
    else:
        return storage.Client()


def upload_to_gcs(file_path: str, blob_name: str) -> str:
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)

    # Ensure bucket exists in fake-gcs-server
    if USE_EMULATOR and not bucket.exists():
        bucket = client.create_bucket(BUCKET_NAME)

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    if USE_EMULATOR:
        # Construct URL manually (no signed URL support in emulator)
        return f"{os.getenv('GCS_EMULATOR_HOST').replace('gcs', 'localhost')}/download/storage/v1/b/{BUCKET_NAME}/o/{blob_name}"
    else:
        return blob.generate_signed_url(version="v4", expiration=3600, method="GET")
