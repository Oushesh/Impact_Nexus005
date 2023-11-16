import os
import pandas as pd
import json
from pathlib import Path

import os
import pandas as pd
import json

def find_files_in_folder(folder_path):
    # Recursively find all files in the folder and its subfolders
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def convert_to_parquet(folder_path, input_paths, main_output_folder):
    for input_path in input_paths:
        # Check if the file is empty
        if os.path.getsize(input_path) == 0:
            print(f"Skipping empty file: {input_path}")
            continue

        # Determine file format based on file extension
        file_extension = input_path.split('.')[-1].lower()
        file_name = input_path.split(".")[0].split("/")[-1].lower()
        try:
            if file_extension in ['csv', 'tsv', 'txt']:
                # CSV, TSV, TXT to Parquet
                sep = '\t' if file_extension == 'tsv' else ',' if file_extension == 'csv' else None
                df = pd.read_csv(input_path, sep=sep, header=None)
                if df.shape[1] == 1:
                    df.columns = ['HEADER']

                output_folder_path = os.path.join(main_output_folder,input_path.split(folder_path)[-1])
                os.makedirs(os.path.dirname(output_folder_path), exist_ok=True)

                output_path = os.path.join(output_folder_path,file_name+".parquet")

            elif file_extension == 'json':
                # JSON to Parquet
                df = pd.read_json(input_path)

                output_folder_path = os.path.join(main_output_folder,input_path.split(folder_path)[-1])
                os.makedirs(os.path.dirname(output_folder_path), exist_ok=True)
                output_path = os.path.join(output_folder_path,file_name+".parquet")

            elif file_extension == 'jsonl':
                # JSONL to Parquet
                data = []
                with open(input_path, 'r') as file:
                    for line in file:
                        data.append(json.loads(line))
                df = pd.DataFrame(data)

                output_folder_path = os.path.join(main_output_folder,input_path.split(folder_path)[-1])
                os.makedirs(os.path.dirname(output_folder_path), exist_ok=True)

                output_path = os.path.join(output_folder_path,file_name+".parquet")

            elif file_extension == 'xlsx':
                # Excel (xlsx) to Parquet
                df = pd.read_excel(input_path, header=None)
                if df.shape[1] == 1:
                    df.columns = ['HEADER']
                output_folder_path = os.path.join(main_output_folder,input_path.split(folder_path)[-1])
                os.makedirs(os.path.dirname(output_folder_path), exist_ok=True)

                output_path = os.path.join(output_folder_path,file_name+".parquet")

            else:
                print(f"Unsupported file format: {file_extension}")
                continue

            # Convert all columns to strings
            df = df.applymap(str)

            # Fill missing data with "None"
            df = df.applymap(lambda x: x if pd.notnull(x) else 'None')

            # Convert column names to strings
            df.columns = df.columns.astype(str)

            # Write DataFrame to Parquet
            df.to_parquet(output_path)

        except pd.errors.ParserError as e:
            print(f"Error parsing {file_extension} file {input_path}: {e}")
            # Handle the error as needed (skip the file, log the error, etc.)

if __name__ == "__main__":
    # Example usage:
    BASE_DIR = Path(__file__).resolve().parent.parent
    input_folder = os.path.join(BASE_DIR,"services_app/KnowledgeBase")  # Replace with your input folder
    print (input_folder)
    output_folder = os.path.join(BASE_DIR,"services_app/KnowledgeBaseParquet")  # Replace with your desired output folder

    # Find all files in the input folder and its subfolders
    input_files = find_files_in_folder(input_folder)
    # Convert each file to Parquet and save it in the output folder
    convert_to_parquet(input_folder,input_files, output_folder)