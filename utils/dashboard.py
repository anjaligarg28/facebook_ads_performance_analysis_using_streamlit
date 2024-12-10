import streamlit as st
import pandas as pd
import emoji

from utils.analyse_and_clean import preprocess

def design_sidebar(data: pd.DataFrame):
    # how the dashboard will look like
    st.write(emoji.emojize("## :arrow_left: Filter the entire data based on your requirement."))

    data["Accident Date"] = pd.to_datetime(data["Accident Date"])
    min_date = data["Accident Date"].min()
    max_date = data["Accident Date"].max()

    # Taking date input from the user
    selected_start_date = st.sidebar.date_input("Select Start Date", value=min_date, key=f"startdate{id}")
    selected_end_date = st.sidebar.date_input("Select End Date", value=max_date, key=f"enddate{id}")

    t1 = pd.to_datetime((str(selected_start_date.day) + "-" + str(selected_start_date.month) + "-" + str(selected_start_date.year)), dayfirst=True)
    t2 = pd.to_datetime((str(selected_end_date.day) + "-" + str(selected_end_date.month) + "-" + str(selected_end_date.year)), dayfirst=True)

    data = data[(data["Accident Date"] >= t1) & (data["Accident Date"] <= t2)]

    preprocessed_data = preprocess(data=data)
    accident_severity = sorted(preprocessed_data["Accident_Severity"].unique().tolist())
    light_conditions = sorted(preprocessed_data["Light_Conditions"].unique().tolist())
    road_surface_condition = sorted(preprocessed_data["Road_Surface_Conditions"].unique().tolist())
    road_type = sorted(preprocessed_data["Road_Type"].unique().tolist())
    area_type = sorted(preprocessed_data["Urban_or_Rural_Area"].unique().tolist())
    weather_condition = sorted(preprocessed_data["Weather_Conditions"].unique().tolist())

    accident_severity.insert(0,"All")
    light_conditions.insert(0,"All")
    road_surface_condition.insert(0,"All")
    road_type.insert(0,"All")
    area_type.insert(0,"All")
    weather_condition.insert(0,"All")

    selected_accident_severity = st.sidebar.selectbox("Select Accident Severity", options=accident_severity)
    selected_light_conditions = st.sidebar.selectbox("Select Light Conditions", options=light_conditions)
    selected_road_surface_condition = st.sidebar.selectbox("Select Road Surface Condition", options=road_surface_condition)
    selected_road_type = st.sidebar.selectbox("Select Road Type", options=road_type)
    selected_area_type = st.sidebar.selectbox("Select Area Type", options=area_type)
    selected_weather_condition = st.sidebar.selectbox("Select Weather Conditions", options=weather_condition)

    # filtering data based on user choice:
    if selected_accident_severity != "All":
        preprocessed_data = preprocessed_data[preprocessed_data["Accident_Severity"] == selected_accident_severity]
    if selected_light_conditions != "All":
        preprocessed_data = preprocessed_data[preprocessed_data["Light_Conditions"] == selected_light_conditions]
    if selected_road_surface_condition != "All":
        preprocessed_data = preprocessed_data[preprocessed_data["Road_Surface_Conditions"] == selected_road_surface_condition]
    if selected_road_type != "All":
        preprocessed_data = preprocessed_data[preprocessed_data["Road_Type"] == selected_road_type]
    if selected_area_type != "All":
        preprocessed_data = preprocessed_data[preprocessed_data["Urban_or_Rural_Area"] == selected_area_type]
    if selected_weather_condition != "All":
        preprocessed_data = preprocessed_data[preprocessed_data["Weather_Conditions"] == selected_weather_condition]

    design_dashboard(preprocessed_data)

def display_initial_metrics(data):

    # Create columns
    col1, col2, col3 = st.columns(3)

    # Use st.metric to display the data points like a card with title and number
    with col1.container(border=True):
        st.metric("Total Number of Accidents", f"{data["Accident_Index"].nunique():,}")

    with col2.container(border=True):
        st.metric("Total Number of Casualties", f"{sum(data["Number_of_Casualties"]):,}")

    with col3.container(border=True):
        st.metric("Total Number of Vehicles Involved", (sum(data["Number_of_Vehicles"])))

    col4, col5, col6 = st.columns(3)
    with col4.container(border=True):
        st.metric("Slight Cases", f"{data[data["Accident_Severity"] == "Slight"]["Accident_Index"].nunique():,}")

    with col5.container(border=True):
        st.metric("Serious Cases", f"{data[data["Accident_Severity"] == "Serious"]["Accident_Index"].nunique():,}")

    with col6.container(border=True):
        st.metric("Fatal Cases", f"{data[data["Accident_Severity"] == "Fatal"]["Accident_Index"].nunique():,}")
    # Using Markdown with custom HTML and CSS for wrapping the text
    st.markdown("""
        <style>
            .metric-box {
                width: 300px;  # Adjust width as needed
                word-wrap: break-word;
                word-break: break-word;
                white-space: normal;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        </style>
        """, unsafe_allow_html=True)

    # Display the metric inside the custom-styled box
    st.markdown(f'<div class="metric-box">This is a very long metric {sum(data["Number_of_Casualties"])} title that will wrap properly inside the box</div>', unsafe_allow_html=True)

def design_dashboard(data):

    display_initial_metrics(data)
