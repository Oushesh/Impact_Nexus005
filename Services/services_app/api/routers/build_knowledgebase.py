import os
from ninja import Router
from pathlib import Path
import json

router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Build_KnowledgeBase():
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @classmethod
    def process_folder(cls,folder_path):
        result = {}

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            if os.path.isdir(item_path):
                result[item] = Build_KnowledgeBase.process_folder(item_path)
            elif os.path.isfile(item_path) and item.endswith(('.csv', '.tsv')):
                result[item] = Build_KnowledgeBase.read_file(item_path)
        return result

    @classmethod
    def read_file(cls,file_path):
        # Assuming you want to read the contents of .csv and .tsv files
        # You might need to adjust this based on the actual file format
        with open(file_path, 'r') as file:
            # Read the content of the file and return it as a list or dictionary
            # For example, if it's a CSV file, you might want to use the csv module
            # If it's a TSV file, you can split lines based on tabs, etc.
            content = file.readlines()
            # Replace contents if they contains /n ot /t
            # Iterate through each line and replace '\n' and '\t'
            for i in range(len(content)):
                content[i] = content[i].replace("\n", "").replace("\t", "")
        return content


@router.get("/build_knowledgebase")
def build_knowledgebase(request,path:str):
    assert isinstance(path,str)

    base_folder = os.path.join(BASE_DIR,"KnowledgeBase/assets")
    output_json = os.path.join(BASE_DIR,"output/knowledge.json")
    #base_folder = '../assets'  # Change this to the root folder of your Django project
    #output_json = 'knowledge.json'  # Change this to the desired output JSON file path

    result = Build_KnowledgeBase.process_folder(base_folder)

    with open(output_json, 'w') as json_file:
        json.dump(result, json_file, indent=4)

    return {"data":"success"}
