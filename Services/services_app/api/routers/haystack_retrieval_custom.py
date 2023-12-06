import os
import json
import logging
from google.cloud import storage
from ninja import Router
from pathlib import Path


router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

logging.basicConfig(level=logging.INFO, filename=os.path.join(BASE_DIR,"logs/haystack_retrieval_custom.log"), filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


logger = logging.getLogger(__name__)


@router("/")
def qa_retrieval(request):
    return {"data":"success"}