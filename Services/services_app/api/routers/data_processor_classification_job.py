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
import random

router = Router()

# Configure logging
log_file_path = "data_processor_classification_logs.log"
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


def fill_train_test_split(df):
    # Fill the "train_test_split" column randomly with "Train" or "Test"
    df['train_test_split'] = df.apply(lambda row: random.choice(['Train', 'Test']), axis=1)
    return df

def assign_labels(df, label_list):
    # Assign labels randomly to the "label" column based on the given list of labels
    df['label'] = random.choices(label_list, k=len(df))
    return df


@router.post("/process_file")
def process_file(request, file: UploadedFile, selected_header: str = '', label_list: str = ''):
    # Get the filename without extension
    filename, _ = file.name.rsplit('.', 1)

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

    # Get the list of headers from the DataFrame
    headers_list = list(df.columns)

    # If no header is selected, provide a list of headers for the user to choose
    if not selected_header:
        return {
            "message": "Please select a header.",
            "headers": headers_list,
        }

    # Check if the selected header exists
    if selected_header not in headers_list:
        return HttpResponse(f"Selected header '{selected_header}' not found in the file.", status=400)

    # Rename the selected header to "text" and move it to the first column
    df['text'] = df[selected_header]
    df.drop(columns=[selected_header], inplace=True)
    df = pd.concat([df['text'], df.drop(columns=['text'])], axis=1)

    # Check if the columns "label" and "train_test_split" already exist
    if 'label' not in df.columns:
        # Add a new "label" column with a default value of "None"
        df['label'] = 'None'

    if 'train_test_split' not in df.columns:
        # Add a new "train_test_split" column with a default value of "None"
        df['train_test_split'] = 'None'

    # Fill the "train_test_split" column randomly with "Train" or "Test"
    df = fill_train_test_split(df)

    # If a label list is provided, assign labels randomly to the "label" column
    if label_list:
        label_list = label_list.split(',')
        df = assign_labels(df, label_list)

    # Save the modified DataFrame to a new Excel file
    output_file = io.BytesIO()
    df.to_excel(output_file, index=False, engine='openpyxl')
    output_file.seek(0)

    # Create a response with the modified file and dynamic filename
    response = HttpResponse(output_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}_filled.xlsx'

    return response