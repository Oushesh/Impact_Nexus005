"""
This is a data loader
and then we perform statistical
check on the data.
"""
import json
import os

import numpy as np
import pandas as pd
import typing as t

from deepchecks.nlp.checks import TextPropertyOutliers
from deepchecks.nlp import TextData


#TODO: rewrite the function into classes

class DisplayEmbeddings:
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    #TODO: add source of data as metadata always and date and time of export or experiment number.
    def read_and_save_data(cls,assets_dir, file_name, url_to_file, file_type='csv', to_numpy=False, include_index=True):
        """If the file exist reads it from the assets' directory, otherwise reads it from the url and saves it."""
        os.makedirs(assets_dir, exist_ok=True)

        #Check if file exists.
        full_file_path = os.path.join(assets_dir,file_name)
        if full_file_path:
            if full_file_path.endswith("csv"):
                try:
                    data = pd.read_csv(full_file_path, index_col=0 if include_index else None)
                except ValueError as e:
                    raise ValueError('csv file does not exist')
            elif full_file_path.endswith("npy"):
                try:
                    data = np.load(full_file_path)
                except ValueError as e:
                    raise ValueError('npy file does not exist')

            elif full_file_path.endswith('json'):
                try:
                    with open(full_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except ValueError as e:
                    raise ValueError('json file does not exist')
            else:
                raise ValueError('file_type must be either "csv" or "npy"')

        if to_numpy and (file_type in {'csv', 'npy'}):
            if isinstance(data, pd.DataFrame):
                data = data.to_numpy()
            elif not isinstance(data, np.ndarray):
                raise ValueError(f'Unknown data type - {type(data)}. Must be either pandas.DataFrame or numpy.ndarray')
        elif to_numpy:
            raise ValueError(f'Cannot convert {file_type} to numpy array')
        return data

    @classmethod
    def load_properties(cls,as_train_test: bool = True):
        """Load and return the properties of the tweet_emotion dataset.

        Parameters
        ----------
        as_train_test : bool, default: True
            If True, the returned data is split into train and test exactly like the toy model
            was trained. The first return value is the train data and the second is the test data.
            In order to get this model, call the load_fitted_model() function.
            Otherwise, returns a single object.

        Returns
        -------
        properties : pd.DataFrame
            Properties for the tweet_emotion dataset.
        """
        ASSETS_DIR = "Data"
        properties = DisplayEmbeddings.read_and_save_data(ASSETS_DIR, 'tweet_emotion_properties.csv', _PROPERTIES_URL, to_numpy=False)
        if as_train_test:
            train = properties[properties['train_test_split'] == 'Train'].drop(columns=['train_test_split'])
            test = properties[properties['train_test_split'] == 'Test'].drop(columns=['train_test_split'])
            return train, test
        else:
            return properties.drop(columns=['train_test_split']).sort_index()

    @classmethod
    def _get_train_test_indexes(cls):
        """Get the indexes of the train and test sets."""

        assets_dir = "Data"
        file_name = "tweet_emotion_data.csv"
        full_file_path = os.path.join(assets_dir,file_name)
        _FULL_DATA_URL = 'https://ndownloader.figshare.com/files/39486889'

        if (full_file_path).exists():
            dataset = pd.read_csv(full_file_path, index_col=0,
                                  usecols=['Unnamed: 0', 'train_test_split'])
        else:
            #Read from url
            dataset = pd.read_csv(_FULL_DATA_URL, index_col=0, usecols=['Unnamed: 0', 'train_test_split'])

        train_indexes = dataset[dataset['train_test_split'] == 'Train'].index
        test_indexes = dataset[dataset['train_test_split'] == 'Test'].index
        return train_indexes, test_indexes

    @classmethod
    def load_embeddings(cls,as_train_test: bool = True) -> t.Union[np.array, t.Tuple[np.array, np.array]]:
        """Load and return the embeddings of the tweet_emotion dataset calculated by OpenAI.

        Parameters
        ----------
        as_train_test : bool, default: True
            If True, the returned data is split into train and test exactly like the toy model
            was trained. The first return value is the train data and the second is the test data.
            Otherwise, returns a single object.

        Returns
        -------
        embeddings : np.ndarray
            Embeddings for the tweet_emotion dataset.
        """
        _EMBEDDINGS_URL = 'https://ndownloader.figshare.com/files/40564880'
        ASSETS_DIR = "Data"
        all_embeddings = DisplayEmbeddings.read_and_save_data(ASSETS_DIR, 'tweet_emotion_embeddings.npy', _EMBEDDINGS_URL,
                                            file_type='npy', to_numpy=True)


        if as_train_test:
            train_indexes, test_indexes = DisplayEmbeddings._get_train_test_indexes()
            return all_embeddings[train_indexes], all_embeddings[test_indexes]
        else:
            return all_embeddings

    @classmethod
    def load_data(cls,data_format: str = 'TextData', as_train_test: bool = True,
                  include_properties: bool = True, include_embeddings: bool = False):
        """Load and returns the Tweet Emotion dataset (classification).

        Parameters
        ----------
        data_format : str, default: 'TextData'
            Represent the format of the returned value. Can be 'TextData'|'DataFrame'
            'TextData' will return the data as a TextData object
            'Dataframe' will return the data as a pandas DataFrame object
        as_train_test : bool, default: True
            If True, the returned data is split into train and test exactly like the toy model
            was trained. The first return value is the train data and the second is the test data.
            In order to get this model, call the load_fitted_model() function.
            Otherwise, returns a single object.
        include_properties : bool, default: True
            If True, the returned data will include the properties of the tweets. Incompatible with data_format='DataFrame'
        include_embeddings : bool, default: True
            If True, the returned data will include the embeddings of the tweets. Incompatible with data_format='DataFrame'

        Returns
        -------
        dataset : Union[TextData, pd.DataFrame]
            the data object, corresponding to the data_format attribute.
        train, test : Tuple[Union[TextData, pd.DataFrame],Union[TextData, pd.DataFrame]
            tuple if as_train_test = True. Tuple of two objects represents the dataset split to train and test sets.
        """
        if data_format.lower() not in ['textdata', 'dataframe']:
            raise ValueError('data_format must be either "TextData" or "Dataframe"')
        elif data_format.lower() == 'dataframe':
            if include_properties or include_embeddings:
                warnings.warn('include_properties and include_embeddings are incompatible with data_format="Dataframe". '
                              'loading only original text data.',UserWarning)
        _FULL_DATA_URL = 'https://ndownloader.figshare.com/files/39486889'
        ASSETS_DIR = "Data"
        _target = 'label'

        data = DisplayEmbeddings.read_and_save_data(ASSETS_DIR, 'tweet_emotion_data.csv', _FULL_DATA_URL, to_numpy=False)
        if not as_train_test:
            data.drop(columns=['train_test_split'], inplace=True)
            if data_format.lower() != 'textdata':
                return data

            metadata = data.drop(columns=[_target, 'text'])
            properties = DisplayEmbeddings.load_properties(as_train_test=False) if include_properties else None
            embeddings = DisplayEmbeddings.load_embeddings(as_train_test=False) if include_embeddings else None
            _CAT_METADATA = ['gender', 'user_region']
            dataset = TextData(data.text, label=data[_target], task_type='text_classification',
                               metadata=metadata, embeddings=embeddings, properties=properties,
                               categorical_metadata=_CAT_METADATA)
            return dataset

        else:
            # train has more sport and Customer Complains but less Terror and Optimism
            train = data[data['train_test_split'] == 'Train'].drop(columns=['train_test_split'])
            test = data[data['train_test_split'] == 'Test'].drop(columns=['train_test_split'])

            if data_format.lower() != 'textdata':
                return train, test

            train_metadata, test_metadata = train.drop(columns=[_target, 'text']), test.drop(columns=[_target, 'text'])
            train_properties, test_properties = DisplayEmbeddings.load_properties(as_train_test=True) if include_properties else (None, None)
            train_embeddings, test_embeddings = DisplayEmbeddings.load_embeddings(as_train_test=True) if include_embeddings else (None, None)

            train_ds = TextData(train.text, label=train[_target], task_type='text_classification',
                                metadata=train_metadata, embeddings=train_embeddings, properties=train_properties,
                                categorical_metadata=_CAT_METADATA)
            test_ds = TextData(test.text, label=test[_target], task_type='text_classification',
                               metadata=test_metadata, embeddings=test_embeddings, properties=test_properties,
                               categorical_metadata=_CAT_METADATA)

            return train_ds, test_ds

if __name__ == "__main__":
    file_name = "tweet_emotion_data.csv"
    assets_dir= "Data"
    url_to_file = "https://ndownloader.figshare.com/files/39486889"
    _PROPERTIES_URL = 'https://ndownloader.figshare.com/files/39717619'
    data = DisplayEmbeddings.read_and_save_data(assets_dir, file_name, url_to_file, file_type='csv', to_numpy=False, include_index=True)
    dataset=DisplayEmbeddings.load_data(as_train_test=False)

    print (data)

    check = TextPropertyOutliers()
    result = check.run(dataset)
    result.show()
    result.save_as_html()


#TODO: add a service to display the results.