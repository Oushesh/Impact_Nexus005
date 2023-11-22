import os
import json


def process_folder(folder_path):
    result = {}

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isdir(item_path):
            result[item] = process_folder(item_path)
        elif os.path.isfile(item_path) and item.endswith(('.csv', '.tsv')):
            result[item] = read_file(item_path)

    return result

def read_file(file_path):
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

def main():
    base_folder = os.path.join(BASE_DIR,"/assets")
    output_json = os.path.join(BASE_DIR,"knowledge.json")

    base_folder = '../assets'  # Change this to the root folder of your Django project
    output_json = 'knowledge.json'  # Change this to the desired output JSON file path

    result = process_folder(base_folder)

    with open(output_json, 'w') as json_file:
        json.dump(result, json_file, indent=4)

if __name__ == "__main__":
    main()


## Data Ingestion, add functions for data injestion from, the folder of knowledge we have.
## Neo4J

## Add Option to to read in headers if possible (TODO)
## Spin Django Services --> Showcase Drag and Drop of new Data into the Django Services (Django)

## ToDO: Setup NLP Check for Embeddings Drift (and connect it with incoming data)
#https://medium.com/@noamzbr/deepchecks-nlp-ml-validation-for-text-made-easy-40aaa8a95c15
