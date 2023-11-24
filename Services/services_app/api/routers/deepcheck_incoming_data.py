"""
This service allows to visualise the
the embeddings and stats from incoming data
It uses but can also be modified to use openai ada embeddings
"""

import os
from ninja import Router
import pandas as pd
import json
import supabase
import logging
import io
from datetime import datetime
import random
from pathlib import Path

from services_app.api.utils.DeepChecks.get_data_properties_deepcheck import DisplayEmbeddings

router = Router()

# Configure logging
log_file_path = "deepcheck_incoming_data.log"
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

## This endpoint works both locally and can be connected to
## any cloud database such as Snowflake, s3 or cloud computing platform

@router.get("/deepcheck")
def deepcheck(request,filename:str,directory="Data"):
    # TODO: fetch processed data from: the other endpoint

    url_to_file = "https://ndownloader.figshare.com/files/39486889"
    _PROPERTIES_URL = 'https://ndownloader.figshare.com/files/39717619'

    data = DisplayEmbeddings.read_and_save_data(directory, filename, file_type='csv', to_numpy=False,                                                include_index=True)
    dataset = DisplayEmbeddings.load_data(as_train_test=False)



    return None


