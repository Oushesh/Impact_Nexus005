"""
This service will optimise the data from 1 s3 to another s3
for optimised costs.
url: of where data is stored. (s3 or google storage or any azure) (you can add new functionalities here and move the logics to utils.py
local path: where data is stored.
"""

import os
from dotenv import load_dotenv
from typing import List
from ninja import Router
from ninja import QueryParam, File
from urllib.parse import urlparse
from django.http import JsonResponse
import pandas as pd
import boto3
from pathlib import Path
import json
from django.shortcuts import get_object_or_404

router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Parquet_Optimization():
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    def find_files_in_subfolders(cls,folder_path):
        # Recursively find all files in subfolders
        files = []
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    @classmethod
    def convert_to_parquet(cls,input_url:str,output_url:str,url_type:str):
        # Determine file format based on file extension
        input_path = urlparse(input_url).path.lstrip('/')
        file_extension = input_path.split('.')[-1].lower()

        if url_type == "local":
            #Loacl path
            df = None
            if file_extension == 'csv':
                df = pd.read_csv(input_path)
            elif file_extension == 'tsv':
                df = pd.read_csv(input_path, sep='\t')
            elif file_extension == 'json':
                df = pd.read_json(input_path)
            elif file_extension == 'jsonl':
                data = []
                with open(input_path, 'r') as file:
                    for line in file:
                        data.append(json.loads(line))
                df = pd.DataFrame(data)
            else:
                #TODO: error handling here with try-exception and put on logger (keep log session onto: redis or so)
                print ("File format not supported")

            if df is not None:
                # Create output folder structure if needed
                output_folder = urlparse(output_url).path.lstrip('/')
                os.makedirs(output_folder, exist_ok=True)

                # Write DataFrame to Parquet
                output_path = os.path.join(output_folder, f"{file_extension}.parquet")
                df.to_parquet(output_path)
                return JsonResponse({"message": f"Conversion successful. Parquet file saved at: {output_path}"})

        #TODO: its possible to add support to extend to other cloud services
        # when your credits is running away during the product-market fit phase
        elif url_type == "s3":
            s3 = boto3.client("s3")
            bucket_name = urlparse(output_url).netloc
            key = urlparse(output_url).path.lsstrip("/")

            # Check if the folder structure exists in the S3 bucket
            response = s3.list_objects(Bucket=bucket_name, Prefix=key)
            if 'Contents' in response:
                return JsonResponse({"message": f"Folder structure already exists in S3 bucket: {bucket_name}/{key}"})
            else:
                s3.put_object(Bucket=bucket_name, Key=key)
                return JsonResponse({"message": f"Creating folder structure in S3 bucket: {bucket_name}/{key}"})

            df = None
            if file_extension == 'csv':
                df = pd.read_csv(input_path)
            elif file_extension == 'tsv':
                df = pd.read_csv(input_path, sep='\t')
            elif file_extension == 'json':
                df = pd.read_json(input_path)
            elif file_extension == 'jsonl':
                data = []
                with open(input_path, 'r') as file:
                    for line in file:
                        data.append(json.loads(line))
                df = pd.DataFrame(data)

            if df is not None:
                # Write DataFrame to Parquet in S3
                s3_parquet_key = os.path.join(key, f"{file_extension}.parquet")
                s3_parquet_url = f"s3://{bucket_name}/{s3_parquet_key}"
                df.to_parquet(s3_parquet_url)
                return JsonResponse({"message": f"Conversion successful. Parquet file saved to S3: {s3_parquet_url}"})

@router.get("/parquet_conversion_service")
def parquet_conversion_service(request, input_url: str, output_url: str, url_type: str = QueryParam('local', alias='url_type')):
    Parquet_Optimization.convert_to_parquet(input_url,output_url,url_type)
    return {"data":"success"}

