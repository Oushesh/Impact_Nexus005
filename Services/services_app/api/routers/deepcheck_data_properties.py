"""
This service allows to visualise the
the embeddings and stats from incoming data
It uses but can also be modified to use openai ada embeddings
"""

import os

import pandas
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
from deepchecks.nlp import TextData
from deepchecks.nlp.checks import TextPropertyOutliers


router = Router()

# Configure logging
log_file_path = "deepcheck_incoming_data.log"
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

## This endpoint works both locally and can be connected to
## any cloud database such as Snowflake, s3 or cloud computing platform


clsss Compute_Data_Properties:
    def __init__(self,**kwargs):
        self.kwargs = kwargs


    @classmethod
    def compute_properties(cls,filepath:str):
        #TODO: test if filepath is indeed a path
        data = pandas.read_csv(filepath)

        try:
            text_data = TextData(data["text"])
        except Exception as error:
            # Handle the exception here
            print(f"Error: {error}")

        #TODO: we have a schema for the definition of the incoming data
        text_data.calculate_builtin_properties()
        TextPropertyOutliers().run(text_data)
        text_data.save_properties(f"{filepath}_properties.csv")

        check = TextPropertyOutliers()
        result = check.run(text_data)
        result.save_as_html(file=os.path.join(filepath.split(".csv")[0],"_properties.html"))
        result.to_wandb()

        return None

@router.get("/deepcheck"))
def deepcheck(request,filename:str,url:directory="Data"):
    # TODO: fetch processed data from: the other endpoint


    Compute_Data_Properties.compute_properties()

    return None


