"""
This service allows to visualise the
the embeddings and stats from incoming data
It uses  but can also be modified to use openai ada embeddings
"""

from ninja import Router
from ninja.files import UploadedFile

import pandas as pd
import logging
import io
from deepchecks.nlp import TextData
from deepchecks.nlp.checks import TextPropertyOutliers
from django.http import JsonResponse, HttpResponse

# Configure logging
log_file_path = "deepcheck_incoming_data.log"
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
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

        # Use pandas to read CSV data from the file content
        data = pd.read_csv(io.StringIO(file_content.decode('utf-8')))

        try:
            text_data = TextData(data["text"])
        except Exception as error:
            # Handle the exception here
            print(f"Error: {error}")

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

        # TODO: modify return here
        return HttpResponse(f"File {file.name} processed successfully", status=200)


@router.post("/deepcheck")
def deepcheck(request, file: UploadedFile):
    filename, _ = file.name.rsplit('.', 1)

    if file.name.endswith(".csv"):
        Data_Properties.compute(file)
        return JsonResponse({"message": f"File {filename} processed successfully"}, status=200)
    else:
        return JsonResponse({"message":f"File {filename} not in .csv format"})


##

