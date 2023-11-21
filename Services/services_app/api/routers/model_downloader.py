"""
Endpoint to download model
from download_blink.sh
"""
import os
from ninja import Router
import urllib.request
from django.http import JsonResponse

router = Router()

MODELS = [
    "biencoder_wiki_large.bin",
    "biencoder_wiki_large.json",
    "entity.jsonl",
    "all_entities_large.t7",
    "crossencoder_wiki_large.bin",
    "crossencoder_wiki_large.json"
]


def download_model(model_file, output_dir):
    root_dir = os.path.realpath(os.path.dirname(__file__))
    dst_dir = os.path.join(root_dir, output_dir)
    os.makedirs(dst_dir, exist_ok=True)

    file_path = os.path.join(dst_dir, model_file)
    url = f"http://dl.fbaipublicfiles.com/BLINK/{model_file}"

    if not os.path.isfile(file_path):
        print(f"Downloading {model_file}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"{model_file} downloaded successfully.")

    return None

@router.get("/model_downloader")
def model_downloader(request,model_name:str):
    #Build the script for downloader here
    if model_name not in MODELS:
        return JsonResponse(content={"error": "Invalid model name"}, status_code=400)
    return {"data":"success"}

## TODO: move all of that script here.
