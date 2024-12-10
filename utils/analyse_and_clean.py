import pandas as pd

def print_unique_values(data: pd.DataFrame):
    columns = data.columns
    for column in columns:
        print(column, ":", data[column].unique())

def preprocess(data: pd.DataFrame):

    # drop duplicates if any
    data = data.drop_duplicates()

    # correcting auto traffic sigl to auto traffic signal in junction control column
    data.loc[:, "Junction_Control"] = data["Junction_Control"].str.replace("Auto traffic sigl", "Auto traffic signal")

    # correcting fetal to fatal in accident severity
    data.loc[:, "Accident_Severity"] = data["Accident_Severity"].str.replace("Fetal", "Fatal")

    # replacing null value in road surface condition column to Not Available
    data.loc[:, "Road_Surface_Conditions"] = data["Road_Surface_Conditions"].fillna("Not Available")

    # replacing null value in road type column to Not Available
    data.loc[:, "Road_Type"] = data["Road_Type"].fillna("Not Available")

    # replacing null value in weather conditions column to Not Available
    data.loc[:, "Weather_Conditions"] = data["Weather_Conditions"].fillna("Not Available")

    # Light_Conditions
    # ['Daylight' 'Darkness - lights lit' 'Darkness - lighting unknown'
    #  'Darkness - lights unlit' 'Darkness - no lighting']

    # Vehicle_Type
    return data
