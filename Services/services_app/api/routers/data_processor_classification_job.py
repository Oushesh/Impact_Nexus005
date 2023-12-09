"""
Service converts any raw data in the form of .csv, .tsv or any excel sheet into ready for the job data.
"""
import os
from ninja import Router
from ninja.files import UploadedFile
import pandas as pd
import logging
import io
from django.http import HttpResponse
import random
from pathlib import Path
from google.cloud import storage
from services_app.api.utils.utils import upload_logs_to_gcs

router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configure logging
logging.basicConfig(level=logging.INFO, filename=os.path.join(BASE_DIR,"logs/data_processor_classification_job.log"), filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


class Classification_Job:
    """
    A classification in NLP usually consists of data in pandas
    predefined which row is for test,train or validation, y-label output,
    either single entry for x as input or multiple rows as input.
    Entity Recognition is also a classification job.
    """
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    #TODO: in reality we need a real data here.
    @classmethod
    def fill_train_test_split(cls,df):
        # Fill the "train_test_split" column randomly with "Train" or "Test"
        df['train_test_split'] = df.apply(lambda row: random.choice(['Train', 'Test']), axis=1)
        logging.info (f"Successfully added split train_test")
        return df


    @classmethod
    def assign_labels(cls,df, label_list):
        # Assign labels randomly to the "label" column based on the given list of labels
        df['label'] = random.choices(label_list, k=len(df))
        logging.info (f"Data assigned to labels")
        return df

@router.post("/process_file")
def process_file(request, file: UploadedFile, selected_header: str = ''):
    # Get the filename without extension
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    local_log_path = os.path.join(BASE_DIR,"logs/data_processor_classification_job.log")

    filename, _ = file.name.rsplit('.', 1)

    input_path = os.path.join(BASE_DIR, "Classification/source/")
    output_path = os.path.join(os.path.join(BASE_DIR, "Classification/target"),filename+"_filled.csv")


    #TODO: Define a list of labels for the data
    label_list = ["Environmental Positive","Environmental Negative","Social Positive","Social Negative","Governance Positive","Governance Negative"]

    # Read the file into a Pandas DataFrame
    if file.name.endswith('.xlsx'):
        df = pd.read_excel(file.file, engine='openpyxl')
    elif file.name.endswith(('.csv', '.tsv')):
        delimiter = '\t' if file.name.endswith('.tsv') else ','
        df = pd.read_csv(io.StringIO(file.file.read().decode('utf-8')), delimiter=delimiter)
    else:
        logging.error(f"Unsupported file format. Please upload a CSV, TSV, or Excel file.status=400")
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
        logging.error (f"Selected header '{selected_header}' not found in the file.status=400")
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
    df = Classification_Job.fill_train_test_split(df)

    # If a label list is provided, assign labels randomly to the "label" column
    if label_list:
        df = Classification_Job.assign_labels(df, label_list)

    # Save the modified DataFrame to a new Excel file
    output_file = io.BytesIO()

    df.to_csv(output_file,index=False)
    df.to_csv()
    output_file.seek(0)

    # Create a response with the modified file and dynamic filename
    response = HttpResponse(output_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}_filled.csv'

    logging.info(f"Successfully transformed the data")

    # TODo: upload the conversion job to
    #Classification_Job.upload_logs_to_gcs(local_log_path,"logs_impactnexus","data_processor_classification_job/data_processor_classification_job.log")
    upload_logs_to_gcs(logging,local_log_path, "logs_impactnexus",
                       "data_processor_classification_job/data_processor_classification_job.log")
    return response


