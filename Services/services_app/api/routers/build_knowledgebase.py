import os
import json
import logging
from google.cloud import storage
from ninja import Router
from pathlib import Path

router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configure logging
logging.basicConfig(filename=os.path.join(BASE_DIR,"build_knowledgebase.log"),level=logging.INFO)
logger = logging.getLogger(__name__)

class Build_KnowledgeBase:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @classmethod
    def process_folder(cls, folder_path):
        log_messages = []
        result = {}
        log_messages.append(f"Processing folder: {folder_path}")
        logging.info (log_messages)
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            if os.path.isdir(item_path):
                result[item] = Build_KnowledgeBase.process_folder(item_path)
            elif os.path.isfile(item_path) and item.endswith(('.csv', '.tsv')):
                # Append log messages from read_file
                result[item], file_log_messages = Build_KnowledgeBase.read_file(item_path, folder_path)
                result = Build_KnowledgeBase.read_file(item_path, folder_path)

                log_messages.extend(file_log_messages)

        return result

    @classmethod
    def read_file(cls, file_path, folder_path):
        log_messages = []
        log_messages.append(f"Reading file: {file_path}")
        logging.info(log_messages)
        try:
            with open(file_path, 'r') as file:
                content = [line.strip().replace("\t", "") for line in file]
                for line in content:
                    log_messages.append(f"Successfully read {file_path}: {line}")

            return {
                "folder_path": folder_path,
                "subfolder_path": os.path.relpath(file_path, BASE_DIR),
                "filename": os.path.basename(file_path),
                "content": content,
            }

        except Exception as e:
            error_message = f"Error opening file {folder_path} {file_path}: {e}"
            logging.error(error_message)


    @classmethod
    def upload_logs_to_gcs(cls, local_log_path, bucket_name, remote_log_path):
        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)

            blob = bucket.blob(remote_log_path)
            blob.upload_from_filename(local_log_path)

            logging.info(f"Logs uploaded to GCS: gs://{bucket_name}/{remote_log_path}")

        except Exception as e:
            logging.error(f"Error uploading logs to GCS: {e}")

@router.get("/build_knowledgebase")
def build_knowledgebase(request, folder_path: str):
    assert isinstance(folder_path, str)

    base_folder = os.path.join(BASE_DIR, folder_path)
    output_json = os.path.join(BASE_DIR, "output/knowledge.json")
    local_log_path = os.path.join(BASE_DIR, "output/logs.txt")

    logging.info(f"Building knowledge base from {base_folder}")

    result = Build_KnowledgeBase.process_folder(base_folder)


    # TODO: Upload logs to Google Cloud Storage
    #Build_KnowledgeBase.upload_logs_to_gcs(local_log_path, "logs_impactnexus/build_knowledgebase", "logs.txt")
    logging.info(f"Knowledge base built successfully. Output: {output_json}")

    with open(output_json, 'w') as json_file:
        json.dump(result, json_file, indent=4)

    return {"data": "success"}
