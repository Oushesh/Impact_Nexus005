import os
from ninja import Router
from pathlib import Path
import json

router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Build_KnowledgeBase:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @classmethod
    def process_folder(cls, folder_path):
        result = {}

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            if os.path.isdir(item_path):
                result[item] = Build_KnowledgeBase.process_folder(item_path)
            elif os.path.isfile(item_path) and item.endswith(('.csv', '.tsv')):
                result[item] = Build_KnowledgeBase.read_file(item_path, folder_path)

        return result

    @classmethod
    def read_file(cls, file_path, folder_path):
        # Assuming you want to read the contents of .csv and .tsv files
        # You might need to adjust this based on the actual file format
        with open(file_path, 'r') as file:
            # If it's a TSV file, you can split lines based on tabs, etc.
            content = file.readlines()
            # Iterate through each line and replace '\n' and '\t'
            for i in range(len(content)):
                content[i] = content[i].replace("\n", "").replace("\t", "")

        # Add folder, subfolder, and filename to the data structure
        return {
            "folder_path": folder_path,
            "subfolder_path": os.path.relpath(file_path, BASE_DIR),
            "filename": os.path.basename(file_path),
            "content": content,
        }

@router.get("/build_knowledgebase")
def build_knowledgebase(request, folder_path:str):
    assert isinstance(folder_path, str)

    # Combine the specified folder path with the base directory
    base_folder = os.path.join(BASE_DIR, folder_path)
    output_json = os.path.join(BASE_DIR, "output/knowledge.json")

    result = Build_KnowledgeBase.process_folder(base_folder)

    with open(output_json, 'w') as json_file:
        json.dump(result, json_file, indent=4)

    return {"data": "success"}
