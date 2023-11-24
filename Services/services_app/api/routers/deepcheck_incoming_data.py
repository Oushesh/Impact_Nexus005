"""
This service allows to visualise the
the embeddings and stats from incoming data
It uses but can also be modified to use openai ada embeddings
"""

import os
from ninja import Router
import pandas as pd
import json
import supbase
import logging
import io
from datetime import datetime
import random
from pathlib import Path

from Services.services_app.utils.DeepChecks.get_data_properties_deepcheck import DisplayEmbeddings

router = Router()

# Configure logging
log_file_path = "deepcheck_incoming_data.log"
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

@router.get("/deepcheck")
def deepcheck(request,directory):
    # TODO: run like a cron job


    return None


