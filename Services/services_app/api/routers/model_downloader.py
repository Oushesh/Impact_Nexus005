"""
Endpoint to download model
from download_blink.sh
"""
import os
from ninja import Router
import urllib.request
from django.http import JsonResponse
import logging
from pathlib import Path
from google.cloud import storage
from services_app.api.utils.utils import upload_logs_to_gcs

router = Router()

MODELS = [
    "biencoder_wiki_large.bin",
    "biencoder_wiki_large.json",
    "entity.jsonl",
    "all_entities_large.t7",
    "crossencoder_wiki_large.bin",
    "crossencoder_wiki_large.json"
]

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configure logging
logging.basicConfig(level=logging.INFO, filename=os.path.join(BASE_DIR,"logs/model_downloader.log"), filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

class Model_Downloader:
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    def download_model(model_file, output_dir):
        root_dir = os.path.realpath(os.path.dirname(__file__))
        dst_dir = os.path.join(root_dir, output_dir)
        os.makedirs(dst_dir, exist_ok=True)

        file_path = os.path.join(dst_dir, model_file)
        print (file_path)
        url = f"http://dl.fbaipublicfiles.com/BLINK/{model_file}"

        if not os.path.isfile(file_path):
            print(f"Downloading {model_file}...")
            logging.info(f"Downloading {model_file}...")
            urllib.request.urlretrieve(url, file_path)
            print(f"{model_file} downloaded successfully.")
            logging.info(f"{model_file} downloaded successfully.")
        return None

@router.get("/model_downloader")
def model_downloader(request,model_name:str):
    assert isinstance(model_name,str)

    local_log_path = os.path.join(BASE_DIR,"logs/model_downloader.log")

    if model_name not in MODELS:
        logging.error("error: Invalid model name, status_code=400")

        #Model_Downloader.upload_logs_to_gcs(local_log_path,"log_impactnexus","model_downloader/model_downloader.log")
        upload_logs_to_gcs(logging,local_log_path, "log_impactnexus", "model_downloader/model_downloader.log")
        return JsonResponse(content={"error": "Invalid model name"}, status_code=400)

    logging.info("success")
    #Model_Downloader.upload_logs_to_gcs(local_log_path,"log_impactnexus","model_downloader/model_downloader.log")
    upload_logs_to_gcs(logging,local_log_path, "log_impactnexus", "model_downloader/model_downloader.log")
    return {"data":"success"}