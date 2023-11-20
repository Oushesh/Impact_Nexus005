import os
import pandas as pd
import json
from pathlib import Path
import logging
from dotenv import load_dotenv
import supabase
from datetime import datetime

## Get the key needed:

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)
supabase_url = os.getenv("supabase_url")
supabase_anon_key = os.getenv("supabase_anon_key")

supabase_project = supabase.Client(supabase_url, supabase_anon_key)

# Configure Logging
log_file_path = 'conversion_logs.log'
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def find_files_in_folder(folder_path):
    # Recursively find all files in the folder and its subfolders
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def convert_to_parquet(input_base_folder, input_file_paths, output_base_folder):
    log_data = {'log_timestamp': [], 'log_level': [], 'log_message': []}
    for input_file_path in input_file_paths:
        # Check if the file is empty
        if os.path.getsize(input_file_path) == 0:
            #Add logger here
            print(f"Skipping empty file: {input_file_path}")
            logger.warning(f"Skipping empty file: {input_file_path}")

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Parse log lines and prepare data for upsert
            log_data['log_timestamp'].append(timestamp)
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
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'Error creating the directory: {e}')
                    logger.warning(f'Error creating the directory: {e}')
                    log_data['log_timestamp'].append(timestamp)
                    log_data["log_level"].append("warning")
                    log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])

            elif file_extension == 'json':
                # JSON to Parquet
                df = pd.read_json(input_file_path)

                try:
                    os.makedirs(output_folder, exist_ok=True)
                except OSError as e:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'Error creating the directory: {e}')
                    logger.warning(f'Error creating the directory: {e}')
                    log_data["log_timestamp"].append(timestamp)
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
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'Error creating the directory: {e}')
                    logger.warning(f'Error creating the directory: {e}')
                    log_data["log_timestamp"].append(timestamp)
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
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'Error creating the directory: {e}')
                    logger.warning(f'Error creating the directory: {e}')
                    log_data["log_timestamp"].append(timestamp)
                    log_data["log_level"].append("warning")
                    log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])

            else:
                print(f"Unsupported file format: {file_extension}")
                logger.warning(f"Unsupported file format: {file_extension}")
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                log_data["log_timestamp"].append(timestamp)
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
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            log_data["log_timestamp"].append(timestamp)
            log_data["log_level"].append("info")
            log_data["log_message"].append(f"Converted {file_extension} file: {input_file_path} to Parquet: {os.path.join(output_folder,output_file_name)}"[:1023])

        except pd.errors.ParserError as e:
            print(f"Error parsing {file_extension} file {input_file_path}: {e}")
            logger.error(f"Error parsing {file_extension} file {input_file_path}: {e}")
            # Handle the error as needed (skip the file, log the error, etc.)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_data["log_timestamp"].append(timestamp)
            log_data["log_level"].append("error")
            log_data["log_message"].append(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])

    # Create a DataFrame from the parsed data
    log_df = pd.DataFrame(log_data).to_dict()
    # Upsert data into the Supabase table
    #supabase_project.table("logs").upsert([{"log_timestamp":"2023-11-17 01:00:00","log_level":"info","log_message":"Test message"}]).execute()
    supabase_project.table('logs').upsert(log_df).execute()

    # Retrieve data from the Supabase table
    query = supabase_project.table('logs').select('*')
    result = query.execute()

    # Print the result
    print(result['data'])

if __name__ == "__main__":
    # Example usage:
    BASE_DIR = Path(__file__).resolve().parent.parent
    input_base_folder = os.path.join(BASE_DIR,"services_app/KnowledgeBase")  # Replace with your input folder

    print ("input_folder",input_base_folder)
    output_base_folder = os.path.join(BASE_DIR,"services_app/KnowledgeBaseParquet")  # Replace with your desired output folder

    print ("output_folder",output_base_folder)
    # Find all files in the input folder and its subfolders
    input_file_paths = find_files_in_folder(input_base_folder)
    print ("input_file",input_file_paths[10])
    # Convert each file to Parquet and save it in the output folder
    convert_to_parquet(input_base_folder,input_file_paths, output_base_folder)

## TODO: add sync between 2 aws s3 Buckets
## TODO: upload log files: # Parse log lines and prepare data for upsert
## TODO: data = {'log_timestamp': [], 'log_level': [], 'log_message': []}

## Airbyte: https://medium.com/@kfinkels/streaming-data-from-multiple-sources-using-airbyte-part-2-c1a00d195cde

## https://medium.com/@kfinkels/streaming-data-from-multiple-sources-using-airbyte-part-2-c1a00d195cde

## Trigger embeddings when new data comes.