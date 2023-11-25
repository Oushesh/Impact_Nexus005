"""
This service allows to visualise the
the embeddings and stats from incoming data
It uses but can also be modified to use openai ada embeddings
"""

from ninja import Router
from ninja import File

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
from django.http import JsonResponse

# Configure logging
log_file_path = "deepcheck_incoming_data.log"
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

## This endpoint works both locally and can be connected to
## any cloud database such as Snowflake, s3 or cloud computing platform




router = Router()

class Data_Properties:
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    def compute(cls, file):
        # Access the file content using file.read()
        file_content = file.read()

        # Use pandas to read CSV data from the file content
        data = pd.read_csv(io.StringIO(file_content.decode('utf-8')))

        try:
            text_data = TextData(data["text"])
        except Exception as error:
            # Handle the exception here
            print(f"Error: {error}")
            return JsonResponse({"message": f"Error processing file: {str(error)}"}, status=500)

        # TODO: Define a schema for the incoming data
        text_data.calculate_builtin_properties()
        TextPropertyOutliers().run(text_data)

        # Save properties using the original filename
        properties_filename = f"{file.name}_properties.csv"
        text_data.save_properties(properties_filename)

        check = TextPropertyOutliers()
        result = check.run(text_data)

        # Save result as HTML using the original filename
        html_filename = f"{file.name.split('.csv')[0]}_properties.html"
        result.save_as_html(file=html_filename)
        result.to_wandb()

        #TODO: modify return here
        return None

@router.post("/deepcheck_endpoint")
def deepcheck(request, file: File):
    Data_Properties.compute(file)
    return JsonResponse({"message":"File processed successfully"},status=200)

## TODO: Complete this endpoint.
## https://github.com/edemiraydin/snowpark_ml_demo_deepchecks/blob/main/Linear%20Regression%20with%20Snowpark%20and%20DeepChecks.ipynb
## Apache Airflow for automation
