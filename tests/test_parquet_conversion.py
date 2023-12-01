"""
Every Endpoint has a functional test here.
"""
import os
import pandas as pd
import json
import pytest

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
    def convert_to_parquet(cls, input_base_folder, input_file_paths, output_base_folder):
        log_dfs = []
        for input_file_path in input_file_paths:
            # Check if the file is empty
            if os.path.getsize(input_file_path) == 0:
                print(f"Skipping empty file: {input_file_path}"[:1023])
                continue

            # Determine file format based on file extension
            file_extension = input_file_path.split('.')[-1].lower()
            file_name = input_file_path.split(".")[0].split("/")[-1]

            output_file_name = input_file_path.split(".")[0].split("/")[-1].lower() + ".parquet"
            output_relative_folder = input_file_path.split(input_base_folder)[-1].split(
                file_name + "." + file_extension)[0].strip("/")
            output_folder = os.path.join(output_base_folder, output_relative_folder)

            df = pd.DataFrame()  # Initialize df outside the try block

            try:
                if file_extension == "csv":
                    # CSV to Parquet
                    try:
                        df = pd.read_csv(input_file_path, sep=',', header=None, na_values='', keep_default_na=False)
                        if df.shape[1] == 1:
                            df.columns = ['COLUMN']
                    except pd.errors.ParserError as e:
                        print(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])
                        continue

                elif file_extension == "tsv":
                    # TSV to Parquet
                    try:
                        df = pd.read_csv(input_file_path, sep='\t', header=None, na_values='', keep_default_na=False)
                        if df.shape[1] == 1:
                            df.columns = ['COLUMN']
                    except pd.errors.ParserError as e:
                        print(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])
                        continue

                elif file_extension == "txt":
                    # TXT to Parquet
                    try:
                        df = pd.read_fwf(input_file_path, header=None, na_values='', keep_default_na=False)
                        if df.shape[1] == 1:
                            df.columns = ['COLUMN']
                    except pd.errors.ParserError as e:
                        print(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])
                        continue

                elif file_extension == "jsonl":
                    # JSONL to Parquet
                    try:
                        data = []
                        with open(input_file_path, 'r') as file:
                            for line in file:
                                data.append(json.loads(line))
                        df = pd.DataFrame(data)
                    except Exception as e:
                        print(f"Error processing {file_extension} file {input_file_path}: {e}"[:1023])
                        df = pd.DataFrame()  # Create an empty DataFrame in case of error

                elif file_extension == "json":
                    # JSON to Parquet
                    try:
                        df = pd.read_json(input_file_path, lines=True)
                    except pd.errors.ParserError as e:
                        print(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])
                        continue

                else:
                    print(f"Unsupported file format: {file_extension}")
                    continue

                # Replace potential NaN values with "None" before writing to Parquet
                df = df.where(pd.notna(df), "None")

                # Ensure column names are strings
                df.columns = df.columns.astype(str)

                # Drop rows with NaN values before appending to log_dfs
                df = df.dropna()

                # Append only if the DataFrame is not empty after dropping NaN values
                if not df.empty:
                    log_dfs.append(df)

            except pd.errors.ParserError as e:
                print(f"Error parsing {file_extension} file {input_file_path}: {e}"[:1023])

        # Concatenate all DataFrames into a single DataFrame
        final_log_df = pd.concat(log_dfs, ignore_index=True)

        # Drop rows with NaN values from the final DataFrame
        final_log_df = final_log_df.dropna()

        # Check if there are any NaN values in the final DataFrame
        if final_log_df.isnull().values.any():
            print("Warning: NaN values found in the final DataFrame. Rows with NaN values are dropped.")

        # Check if the final DataFrame is not empty
        if not final_log_df.empty:
            # Write the final DataFrame to Parquet
            final_log_df.to_parquet(os.path.join(output_folder, output_file_name))

        return final_log_df


def parquet_conversion_service(url_type:str,input_base_folder:str,output_base_folder:str):
    # TODO: make a way there is drop down for user to select the url_type
    assert url_type in ["local","s3","gs"]

    input_file_paths = Parquet_Optimization.find_files_in_folder(input_base_folder)

    log_df = Parquet_Optimization.convert_to_parquet(input_base_folder,input_file_paths,output_base_folder)
    return log_df


def test_actual_functionality():
    url_type = "local"
    input_base_folder = os.path.join("Services/services_app", "KnowledgeBase")
    output_base_folder = os.path.join("Services/services_app", "KnowledgeBaseParquet")

    # Perform the parquet conversion service
    final_log_df = parquet_conversion_service(url_type, input_base_folder, output_base_folder)
    # Check if there are any NaN values in the final DataFrame

    assert not final_log_df.isnull().values.any(), "No NaN values should exist in the final DataFrame"

