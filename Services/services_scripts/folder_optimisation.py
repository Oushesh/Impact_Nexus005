import os
import pandas as pd
import json
from pathlib import Path

def find_files_in_folder(folder_path):
    # Recursively find all files in the folder and its subfolders
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def convert_to_parquet(input_base_folder, input_file_paths, output_base_folder):
    for input_file_path in input_file_paths:
        # Check if the file is empty
        if os.path.getsize(input_file_path) == 0:
            #Add logger here
            print(f"Skipping empty file: {input_file_path}")
            continue

        # Determine file format based on file extension
        file_extension = input_file_path.split('.')[-1].lower()
        file_name = input_file_path.split(".")[0].split("/")[-1]

        output_file_name = input_file_path.split(".")[0].split("/")[-1].lower() + ".parquet"
        output_relative_folder = input_file_path.split(input_base_folder)[-1].split(file_name+"."+file_extension)[0]
        output_relative_folder = output_relative_folder.strip("/")

        output_folder = os.path.join(output_base_folder,output_relative_folder)
        print (file_name+"."+file_extension)
        print ("file extension",file_extension)
        print ("file name",file_name)
        print ("output file_name",output_file_name)
        print ("output_relative_folder",output_relative_folder)
        print ("input_file_path",input_file_path)
        print ("output_base_folder",output_base_folder)
        print ("output_folder",output_folder)
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
                    print(f'Error creating the directory: {e}')

            elif file_extension == 'json':
                # JSON to Parquet
                df = pd.read_json(input_file_path)

                try:
                    os.makedirs(output_folder, exist_ok=True)
                except OSError as e:
                    print(f'Error creating the directory: {e}')

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
                    print(f'Error creating the directory: {e}')

            elif file_extension == 'xlsx':
                # Excel (xlsx) to Parquet
                df = pd.read_excel(input_file_path, header=None)
                if df.shape[1] == 1:
                    df.columns = ['HEADER']
                try:
                    os.makedirs(output_folder, exist_ok=True)
                except OSError as e:
                    print(f'Error creating the directory: {e}')

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
            df.to_parquet(os.path.join(output_folder,output_file_name))

        except pd.errors.ParserError as e:
            print(f"Error parsing {file_extension} file {input_file_path}: {e}")
            # Handle the error as needed (skip the file, log the error, etc.)

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