import os
from google.cloud import storage

def upload_logs_to_gcs(logging,local_log_path, bucket_name, remote_log_path):
    """
    :param logging: python logger object
    :param local_log_path: path of the log file locally
    :param bucket_name: google cloud bucket name
    :param remote_log_path: path of the file when uploaded.
    :return: None
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)

        blob = bucket.blob(remote_log_path)
        blob.upload_from_filename(local_log_path)

        logging.info(f"Logs uploaded to GCS: gs://{bucket_name}/{remote_log_path}")

    except Exception as e:
        logging.error(f"Error uploading logs to GCS: {e}")