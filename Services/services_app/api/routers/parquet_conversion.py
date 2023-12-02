"""
This service will optimise the data from 1 s3 to another s3
for optimised costs.
url: of where data is stored. (s3 or google storage or any azure) (you can add new functionalities here and move the logics to utils.py
local path: where data is stored.
"""
import os
from ninja import Router
import pandas as pd
from pathlib import Path
import json
import supabase
import logging
from dotenv import load_dotenv
from datetime import datetime
from google.cloud import storage

router = Router()

# Configure logging
BASE_DIR = Path(__file__).resolve().parent.parent.parent
logging.basicConfig(level=logging.INFO, filename="logs/", filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

class Parquet_Optimization():
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    def find_files_in_folder(cls,folder_path):
        # Recursively find all files in the folder and its subfolders
        files = []
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    @classmethod
    def convert_to_parquet(cls,input_base_folder, input_file_paths, output_base_folder):
        #Set Supabase client

        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        dotenv_path = os.path.join(BASE_DIR,".env")
        #print (dotenv_path)
        load_dotenv(dotenv_path)

        supabase_url = os.getenv("supabase_url")
        supabase_anon_key = os.getenv("supabase_anon_key")


        supabase_project = supabase.Client(supabase_url,supabase_anon_key)

        log_data = {'log_level': [], 'log_message': []}
        for input_file_path in input_file_paths:
            # Check if the file is empty
            if os.path.getsize(input_file_path) == 0:
                #Add logger here
                #print(f"Skipping empty file: {input_file_path}")
                logger.warning(f"Skipping empty file: {input_file_path}")

                timestamp = datetime.now()
                #log_data['log_timestamp'].append(timestamp)
                log_data["log_level"].append("warning")
                log_data["log_message"].append(f"Skipping empty file: {input_file_path}"[:1023])
                continue

            # Determine file format based on file extension
            file_extension = input_file_path.split('.')[-1].lower()
            file_name = input_file_path.split(".")[0].split("/")[-1]

            output_file_name = input_file_path.split(".")[0].split("/")[-1].lower() + ".parquet"
            output_relative_folder = input_file_path.split(input_base_folder)[-1].split(file_name+"."+file_extension)[0]
            output_relative_folder = output_relative_folder.strip("/")

            output_folder = os.path.join(output_base_folder,output_relative_folder)
            try:
                if file_extension in ['csv', 'tsv', 'txt']:
                    # CSV, TSV, TXT to Parquet
                    sep = '\t' if file_extension == 'tsv' else ',' if file_extension == 'csv' else None
                    df = pd.read_csv(input_file_path, sep=sep, header=None)
                    if df.shape[1] == 1:
                        df.columns = ['HEADER']

                    try:
                        os.makedirs(output_folder, exist_ok=True)
                    except OSError as e:
                        #print(f'Error creating the directory: {e}')
                        logger.warning(f'Error creating the directory: {e}')
                        timestamp = datetime.now()
                        #log_data['log_timestamp'].append(timestamp)
                        #log_data['log_timestamp'].append("2023-11-17 0DD1:00:00")
                        log_data["log_level"].append("warning")
                        log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])

                elif file_extension == 'json':
                    # JSON to Parquet
                    df = pd.read_json(input_file_path)
                    try:
                        os.makedirs(output_folder, exist_ok=True)
                    except OSError as e:
                        timestamp = datetime.now()
                        #print(f'Error creating the directory: {e}')
                        logger.warning(f'Error creating the directory: {e}')
                        #log_data["log_timestamp"].append(timestamp)
                        #log_data['log_timestamp'].append("2023-11-17 0DD1:00:00")
                        log_data["log_level"].append("warning")
                        log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])


                elif file_extension == 'jsonl':
                    # JSONL to Parquet
                    data = []
                    with open(input_file_path, 'r') as file:
                        for line in file:
                            data.append(json.loads(line))
                    df = pd.DataFrame(data)

                    try:
                        os.makedirs(output_folder, exist_ok=True)
                    except OSError as e:
                        timestamp = datetime.now()
                        #print(f'Error creating the directory: {e}')
                        logger.warning(f'Error creating the directory: {e}')
                        #log_data["log_timestamp"].append(timestamp)
                        #log_data['log_timestamp'].append("2023-11-17 0DD1:00:00")
                        log_data["log_level"].append("warning")
                        log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])

                elif file_extension == 'xlsx':
                    # Excel (xlsx) to Parquet
                    df = pd.read_excel(input_file_path, header=None)
                    if df.shape[1] == 1:
                        df.columns = ['HEADER']
                    try:
                        os.makedirs(output_folder, exist_ok=True)
                    except OSError as e:
                        timestamp = datetime.now()
                        #print(f'Error creating the directory: {e}')
                        logger.warning(f'Error creating the directory: {e}')
                        #log_data["log_timestamp"].append(timestamp)
                        #log_data['log_timestamp'].append("2023-11-17 0DD1:00:00")
                        log_data["log_level"].append("warning")
                        log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])

                else:
                    #print(f"Unsupported file format: {file_extension}")
                    logger.warning(f"Unsupported file format: {file_extension}")
                    timestamp = datetime.now()

                    #log_data["log_timestamp"].append(timestamp)
                    #log_data['log_timestamp'].append("2023-11-17 0DD1:00:00")
                    log_data["log_level"].append("warning")
                    log_data["log_message"].append(f"Unsupported file format: {file_extension}"[:1023])
                    continue

                # Convert all columns to strings
                df = df.applymap(str)

                # Fill missing data with "None"
                df = df.applymap(lambda x: x if pd.notnull(x) else 'None')

                # Convert column names to strings
                df.columns = df.columns.astype(str)

                # Write DataFrame to Parquet
                df.to_parquet(os.path.join(output_folder,output_file_name))
                logger.info(f"Converted {file_extension} file: {input_file_path} to Parquet: {os.path.join(output_folder,output_file_name)}")
                timestamp = datetime.now()

                #log_data["log_timestamp"].append(timestamp)
                #log_data['log_timestamp'].append("2023-11-17 0DD1:00:00")
                log_data["log_level"].append("info")
                log_data["log_message"].append(f"Converted {file_extension} file: {input_file_path} to Parquet: {os.path.join(output_folder,output_file_name)}"[:1023])

            except pd.errors.ParserError as e:
                #print(f"Error parsing {file_extension} file {input_file_path}: {e}")
                logger.error(f"Error parsing {file_extension} file {input_file_path}: {e}")
                # Handle the error as needed (skip the file, log the error, etc.)
                #timestamp = datetime.now()
                #log_data["log_timestamp"].append(timestamp)
                log_data["log_level"].append("error")
                log_data["log_message"].append(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])

        # Create a DataFrame from the parsed data
        log_df = pd.DataFrame(log_data).to_dict()
        #print (log_df)
        # Upsert data into the Supabase table
        supabase_project.table('logs').upsert(log_df).execute()

    @classmethod
    def upload_logs_to_gcs(cls, local_log_path, bucket_name, remote_log_path):
        """
        :param local_log_path: path of the log file locally
        :param bucket_name: google cloud bucket name
        :param remote_log_path: path of the file when uploaded.
        :return: None
        """
        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)

            blob = bucket.blob(remote_log_path)
            blob.upload_from_filename(local_log_path)

            logging.info(f"Logs uploaded to GCS: gs://{bucket_name}/{remote_log_path}")

        except Exception as e:
            logging.error(f"Error uploading logs to GCS: {e}")

@router.get("/parquet_conversion_service")
def parquet_conversion_service(request, url_type:str,input_base_folder:str,output_base_folder:str):
    # TODO: make a way there is drop down for user to select the url_type
    assert url_type in ["local","s3"]
    assert isinstance(input_base_folder,str)
    assert isinstance(output_base_folder,str)
    assert isinstance(url_type,str)

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    input_base_folder = os.path.join(BASE_DIR,"KnowledgeBase")  # Replace with your input folder
    local_log_path = os.path.join(BASE_DIR,"logs/parquet_conversion.log")

    #print ("input_folder",input_base_folder)
    output_base_folder = os.path.join(BASE_DIR,"KnowledgeBaseParquet")

    #print ("output_folder",output_base_folder)

    # Find all files in the input folder and its subfolders
    input_file_paths = Parquet_Optimization.find_files_in_folder(input_base_folder)

    #print (input_file_paths)

    Parquet_Optimization.convert_to_parquet(input_base_folder,input_file_paths,output_base_folder)
    Parquet_Optimization.upload_logs_to_gcs(local_log_path,"logs_impactnexus","parquet_conversion/parquet_conversion.log")
    return {"data":"success"}


#TODO: correct bug with supabase, serve this on cloud