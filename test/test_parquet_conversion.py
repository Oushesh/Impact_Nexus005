"""
Every Endpoint has a functional test here.
"""

from pathlib import Path
import os
import supabase
from dotenv import load_dotenv
import logging
import pandas as pd

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
        log_data = {'log_level': [], 'log_message': []}
        for input_file_path in input_file_paths:
            # Check if the file is empty
            if os.path.getsize(input_file_path) == 0:
                log_data["log_level"].append("warning")
                log_data["log_message"].append(f"Skipping empty file: {input_file_path}"[:1023])
                continue

            # Determine file format based on file extension
            file_extension = input_file_path.split('.')[-1].lower()
            file_name = input_file_path.split(".")[0].split("/")[-1]

            # Build the output folder name from the path of the input files. Maintain same structure between the Input
            # main and Output Main Folders.
            output_file_name = input_file_path.split(".")[0].split("/")[-1].lower() + ".parquet"
            output_relative_folder = input_file_path.split(input_base_folder)[-1].split(file_name+"."+file_extension)[0].strip("/")
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
                        log_data["log_level"].append("warning")
                        log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])

                elif file_extension == 'json':
                    # JSON to Parquet
                    df = pd.read_json(input_file_path)
                    try:
                        os.makedirs(output_folder, exist_ok=True)
                    except OSError as e:
                        logger.warning(f'Error creating the directory: {e}')
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
                        log_data["log_level"].append("warning")
                        log_data["log_message"].append(f'Error creating the directory: {e}'[:1023])

                else:
                    print(f"Unsupported file format: {file_extension}")
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

                log_data["log_level"].append("info")
                log_data["log_message"].append(f"Converted {file_extension} file: {input_file_path} to Parquet: {os.path.join(output_folder,output_file_name)}"[:1023])

            except pd.errors.ParserError as e:
                log_data["log_level"].append("error")
                log_data["log_message"].append(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])

        # Create a DataFrame from the parsed data
        log_df = pd.DataFrame(log_data).to_dict()


def parquet_conversion_service(url_type:str,input_base_folder:str,output_base_folder:str):
    # TODO: make a way there is drop down for user to select the url_type
    assert url_type in ["local","s3"]

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    input_base_folder = os.path.join(BASE_DIR,"KnowledgeBase")  # Replace with your input folder

    output_base_folder = os.path.join(BASE_DIR,"KnowledgeBaseParquet")

    input_file_paths = Parquet_Optimization.find_files_in_folder(input_base_folder)

    Parquet_Optimization.convert_to_parquet(input_base_folder,input_file_paths,output_base_folder)
    return None

def test_parquet_conversion_service():
    url_type = "local"
    input_base_folder = os.path.join("../Services/services_app","KnowledgeBase")
    output_base_folder = os.path.join("../Services/services_app","KnowledgeBaseParquet")

    #Read files and check if they contain NaN etc..
    parquet_conversion_service(url_type,input_base_folder,output_base_folder)
    return None


##TODO: add more test service here.