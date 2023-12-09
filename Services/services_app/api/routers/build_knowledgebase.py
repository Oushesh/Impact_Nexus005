import os
import json
import logging
from ninja import Router
from pathlib import Path
from services_app.api.utils.utils import upload_logs_to_gcs


router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configure logging
logging.basicConfig(level=logging.INFO, filename=os.path.join(BASE_DIR,"logs/build_knowledgebase.log"), filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


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
                result = Build_KnowledgeBase.read_file(item_path, folder_path)
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


@router.get("/build_knowledgebase")
def build_knowledgebase(request, folder_path: str):
    assert isinstance(folder_path, str)

    base_folder = os.path.join(BASE_DIR, folder_path)
    output_json = os.path.join(BASE_DIR, "output/knowledge.json")
    local_log_path = os.path.join(BASE_DIR, "logs/build_knowledgebase.log")

    logging.info(f"Building knowledge base from {base_folder}")

    result = Build_KnowledgeBase.process_folder(base_folder)

    logging.info(f"Knowledge base built successfully. Output: {output_json}")

    with open(output_json, 'w') as json_file:
        json.dump(result, json_file, indent=4)

    upload_logs_to_gcs(logging,local_log_path, "logs_impactnexus","build_knowledgebase/build_knowledgebase.log")
    return {"data": "success"}
