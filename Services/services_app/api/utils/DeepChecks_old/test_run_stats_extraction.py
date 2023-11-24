from deepchecks.nlp.checks import TextPropertyOutliers
from deepchecks.nlp import TextData
from deepchecks.nlp.checks import TextEmbeddingsDrift

import pandas as pd

data = pd.read_csv("Data/dfg_other_sectors_20220121_filled.csv")
text_data = TextData(data["text"])


text_data.calculate_builtin_properties()
result =TextPropertyOutliers().run(text_data)


# Save the properties into a separate .csv file
property_name_file = "properties.csv"
text_data.save_properties(property_name_file)

#TextEmbeddingsDrift.run(text_data)

result.show()
result.save_as_html(file="Data/properties.html")

## Needed: FastText and pybind 11

## Convert this into a service and win.








