"""
This service allows to convert any
raw data in the form of .csv,
.tsv or any excel sheet into ready for the job
data.
"""

import os
from ninja import Router
from ninja.files import UploadedFile
import pandas as pd
from pathlib import Path
import json
import supabase
import logging
import io
from dotenv import load_dotenv
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render

router = Router()

# Configure logging
log_file_path = "data_processor_classification_logs.log"
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

@router.post("/process_file_classification_job")
def process_file_classification_job(request, file: UploadedFile):
    # Read the file into a Pandas DataFrame
    if file.name.endswith('.xlsx'):
        df = pd.read_excel(file.file, engine='openpyxl')
    elif file.name.endswith(('.csv', '.tsv')):
        delimiter = '\t' if file.name.endswith('.tsv') else ','
        df = pd.read_csv(io.StringIO(file.file.read().decode('utf-8')), delimiter=delimiter)
    else:
        return HttpResponse("Unsupported file format. Please upload a CSV, TSV, or Excel file.", status=400)

    # Fill in empty rows with "None"
    df.fillna('None', inplace=True)

    # Save the modified DataFrame to a new Excel file
    output_file = io.BytesIO()
    df.to_excel(output_file, index=False, engine='openpyxl')
    #TODO: save it to csv instead.
    df.to_csv()
    output_file.seek(0)

    # Create a response with the modified file
    response = HttpResponse(output_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=modified_file.xlsx'

    return response
