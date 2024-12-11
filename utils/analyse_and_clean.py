import pandas as pd
import numpy as np
import streamlit as st

def print_unique_values(data: pd.DataFrame):
    columns = data.columns
    for column in columns:
        print(column, ":", data[column].unique())

def create_time_interval_col(data: pd.DataFrame):
    # Convert Time column to datetime format
    data['Time'] = pd.to_datetime(data['Time'], format='%H:%M')

    # Extract the hour
    data['Hour'] = data['Time'].dt.hour
    data["Hour"].replace(np.nan, -1, inplace=True)
    data["Hour"] = data["Hour"].astype(int)

    # Create intervals
    data['Interval'] = data['Hour'].apply(lambda x: f"{str(x).zfill(2)} - {str(x+1).zfill(2)}")
    data["Interval"] = data["Interval"].astype(str)

    return data

def preprocess(data: pd.DataFrame):

    # drop duplicates if any
    data = data.drop_duplicates()
    data["Number_of_Accidents"] = 1

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

    data = create_time_interval_col(data)
    return data

def group_and_aggregate(data: pd.DataFrame, group_on: list, aggregate_on: dict)  -> pd.DataFrame:
    data = data.groupby(group_on).agg(aggregate_on).reset_index()
    return data
