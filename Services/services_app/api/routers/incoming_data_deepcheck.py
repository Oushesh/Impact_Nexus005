"""
This service allows to visualise the
the embeddings and stats from incoming data
It uses  but can also be modified to use openai ada embeddings
"""

from ninja import Router
from ninja.files import UploadedFile

import pandas as pd
import logging
import io,os
from deepchecks.nlp import TextData
from deepchecks.nlp.checks import TextPropertyOutliers
from django.http import JsonResponse, HttpResponse
from pathlib import Path
from google.cloud import storage
from services_app.api.utils.utils import upload_logs_to_gcs

# Configure logging
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configure logging
logging.basicConfig(level=logging.INFO, filename=os.path.join(BASE_DIR,"logs/incoming_data_deepcheck.log"), filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

router = Router()

class Data_Properties:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @classmethod
    def compute(cls, file):
        # Access the file content using file.read()
        file_content = file.read()
        logging.info(f"{file} contents read")
        # Use pandas to read CSV data from the file content
        try:
            data = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
            logging.info(f"{file} ")
        except Exception as error:
            logging.error(error)

        try:
            text_data = TextData(data["text"])
        except Exception as error:
            # Handle the exception here
            print(f"Error: {error}")
            logging.error(error)

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

        logging.info(f"File {file.name} processed successfully,status=200")

        return HttpResponse(f"File {file.name} processed successfully", status=200)


@router.post("/deepcheck")
def deepcheck(request, file: UploadedFile):
    filename, _ = file.name.rsplit('.', 1)

    local_log_path = os.path.join(BASE_DIR, "logs/incoming_data_deepcheck.log")

    if file.name.endswith(".csv"):
        Data_Properties.compute(file)
        logging.info(f"File {filename} processed successfully status=200")
        #Data_Properties.upload_logs_to_gcs(local_log_path,"logs_impactnexus","incoming_data_deepcheck/incoming_data_deepcheck.log")
        upload_logs_to_gcs(local_log_path, "logs_impactnexus", "incoming_data_deepcheck/incoming_data_deepcheck.log")
        return JsonResponse({"message": f"File {filename} processed successfully"}, status=200)
    else:
        logging.error(f"File {filename} not in .csv format")
        #Data_Properties.upload_logs_to_gcs(local_log_path,"logs_impactnexus","incoming_data_deepcheck/incoming_data_deepcheck.log")
        upload_logs_to_gcs(local_log_path, "logs_impactnexus", "incoming_data_deepcheck/incoming_data_deepcheck.log")
        return JsonResponse({"message":f"File {filename} not in .csv format"})



