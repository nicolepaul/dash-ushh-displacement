import pandas as pd

from parsers.parse_data_dictionary import parse_data_dictionary
from parsers.parse_puf_files import custom_puf_handling


def get_data():

    # Load data
    data = pd.read_csv("displaced_households.csv")

    # Read data dictionary
    data_dict_file = "Data_Dictionary.xlsx"
    data_dict = parse_data_dictionary(data_dict_file).set_index('Variable')

    # Implement custom data handling
    data, data_dict = custom_puf_handling(data, data_dict)

    return data, data_dict