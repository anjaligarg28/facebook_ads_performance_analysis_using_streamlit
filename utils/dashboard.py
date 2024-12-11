import streamlit as st
import plotly.express as px
import plotly.io as pio
import pandas as pd
import emoji
import plotly.graph_objects as go
import copy

from utils.analyse_and_clean import preprocess, group_and_aggregate

def design_sidebar(data: pd.DataFrame):
    # how the dashboard will look like
    st.sidebar.write(emoji.emojize(":arrow_down: Filter the entire data based on your requirement."))

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
    col1, col2, col3, col4, col5 = st.columns(5)

    # Use st.metric to display the data points like a card with title and number
    with col1.container(border=True):
        st.metric("Total Number of Accidents", f"{sum(data["Number_of_Accidents"]):,}")

    with col2.container(border=True):
        st.metric("Total Number of Casualties", f"{sum(data["Number_of_Casualties"]):,}")

    with col3.container(border=True):
        st.metric("Slight Accidents", f"{sum(data[data["Accident_Severity"] == "Slight"]["Number_of_Accidents"]):,}")

    with col4.container(border=True):
        st.metric("Serious Accidents", f"{sum(data[data["Accident_Severity"] == "Serious"]["Number_of_Accidents"]):,}")

    with col5.container(border=True):
        st.metric("Fatal Accidents", f"{sum(data[data["Accident_Severity"] == "Fatal"]["Number_of_Accidents"]):,}")

def create_pie_chart(data, names_column, values_column, threshold=2):
    """
    Create a pie chart using Plotly Express in Streamlit.

    Args:
    data (pd.DataFrame): The data for the pie chart.
    names_column (str): The column name for the pie chart categories (labels).
    values_column (str): The column name for the pie chart values (sizes).

    Returns:
    None: Displays the pie chart in Streamlit.
    """
    data = group_and_aggregate(data=data, group_on=[names_column], aggregate_on={values_column:"sum"})
    total_value = data[values_column].sum()
    # Create a new dataframe with "Others" category
    data["percentage"] = (data[values_column] / total_value) * 100
    data[names_column] = data.apply(lambda row: row[names_column] if row["percentage"] >= threshold else "Other", axis=1)

    # Group by category to combine small percentages into "Others"
    data = group_and_aggregate(data = data, group_on = names_column, aggregate_on={values_column:"sum"})
    fig = px.pie(data, names=names_column, values=values_column, title=f"{values_column.replace("_", " ")} by {names_column.replace("_", " ")}")
    # Update layout to reduce the size of the pie chart
    fig.update_layout(
        width=380,  # Adjust width
        height=400,  # Adjust height
        title=dict(font=dict(size=14)),  # Adjust title font size
        # margin=dict(l=20, r=20, t=40, b=20)  # Reduce margins
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="top",
            y=-0.2,  # Adjust to position it below the chart
            xanchor="center",
            x=0.5,  # Center the legend horizontally
        ),
        plot_bgcolor="#222222",
        paper_bgcolor="#222222",
    )
    st.plotly_chart(fig)

def create_rolling_average_chart(data, x_column, y_columns, window=7, title="Rolling Average Chart", height=350):
    """
    Create a multi-line chart for rolling averages using Plotly Express in Streamlit.

    Args:
    data (pd.DataFrame): The data for the chart.
    x_column (str): The column name for the x-axis.
    y_columns (dict): A list of column names for the y-axis values.
    window (int): The window size for the rolling average (default is 3).
    title (str): The title of the chart (optional).

    Returns:
    None: Displays the rolling average chart in Streamlit.
    """
    data = group_and_aggregate(data=data, group_on=[x_column], aggregate_on=y_columns)
    y_columns = list(y_columns.keys())
    # Calculate rolling averages for the specified columns
    for col in y_columns:
        data[col] = data[col].rolling(window=window).mean()
    # Plot the rolling averages as a multi-line chart
    fig = px.line(data, x=x_column, y=y_columns, title=title)
    # Customize the chart layout
    fig.update_layout(
        title=title,  # Set the chart title
        xaxis_title=x_column,  # Set the x-axis title
        yaxis_title="Count",  # Set the y-axis title
        height=height,  # Set the height of the chart
    )
    st.plotly_chart(fig)

def accident_vs_casualties(data):
    col1, col2 = st.columns([0.5,4])
    with col1:
        st.write("   ")
        rolling_window = st.selectbox("Select a rolling average window for smoother trend line:", options=[7,1,15,30])
        st.write("(1 implies plain data points without averaging them out)")
    with col2:
        create_rolling_average_chart(data, "Accident Date", {"Number_of_Accidents":"sum", "Number_of_Casualties":"sum"}, window=rolling_window, title="Trend Line of Accidents and Casualties Over Time")

# Function to create a horizontal bar chart
def create_horizontal_bar_chart(dataframe, dimension_col, metric_cols):
    """
    Create a horizontal bar chart using Plotly with multiple metrics.

    Args:
        dataframe (pd.DataFrame): Input DataFrame containing the data.
        dimension_col (str): Column name for the dimension (categories).
        metric_cols (list of str): List of column names for metrics.

    Returns:
        plotly.graph_objects.Figure: The horizontal bar chart figure.
    """
    fig = go.Figure()

    for metric in metric_cols:
        fig.add_trace(go.Bar(
            y=dataframe[dimension_col],  # Dimension on the Y-axis
            x=dataframe[metric],         # Metric values
            name=metric,                 # Metric name for the legend
            orientation='h'              # Horizontal bars
        ))

    # Update layout
    fig.update_layout(
        title="Horizontal Bar Chart",
        xaxis_title="Value",
        yaxis_title=dimension_col,
        barmode='group',  # Group bars by dimension
        height=400        # Adjust height if needed
    )
    # Display in Streamlit
    st.plotly_chart(fig)

def map(data):
    # Ensure required columns are present
    if all(col in data.columns for col in ["Latitude", "Longitude"]):
        st.sidebar.subheader("Map Filters")
        selected_date = st.sidebar.date_input("Filter by date", value=None)

        if selected_date:
            data = data[pd.to_datetime(data["Accident Date"]).dt.date == selected_date]

        st.write(f"Showing {len(data)} accident points on the map.")

        # Plot scatter map
        fig = px.scatter_mapbox(data, lat="Latitude", lon="Longitude",
                                hover_name="Accident Date",
                                mapbox_style="carto-positron",
                                zoom=10)
        fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    else:
        st.error("The uploaded file must contain 'Latitude' and 'Longitude' columns.")

def casualties_distributions(data):
    col1, col2, col3 = st.columns([1.3,1.5,1.5])
    with col1:
        create_pie_chart(copy.deepcopy(data), "Accident_Severity", "Number_of_Accidents")
        create_pie_chart(copy.deepcopy(data), "Urban_or_Rural_Area", "Number_of_Accidents")
    with col2:
        create_pie_chart(copy.deepcopy(data), "Light_Conditions", "Number_of_Accidents")
        create_pie_chart(copy.deepcopy(data), "Weather_Conditions", "Number_of_Accidents")
    with col3:
        create_pie_chart(copy.deepcopy(data), "Road_Surface_Conditions", "Number_of_Accidents")
        create_pie_chart(copy.deepcopy(data), "Vehicle_Type", "Number_of_Accidents")

def create_side_by_side_barchart(data, category_col, metric1_col: str, metric2_col):
    """
    Create a side-by-side bar chart using Plotly and Streamlit.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        category_col (str): Column name for categories (x-axis).
        metric1_col (str): Column name for Metric 1.
        metric2_col (str): Column name for Metric 2.
        chart_title (str): Title for the chart.
    """
    chart_title = f"{metric1_col.replace("_", " ")} and {metric2_col.replace("_", " ")} by {category_col.replace("_", " ")}"
    data[category_col] = data[category_col].astype(str)
    data = group_and_aggregate(data=data, group_on=[category_col], aggregate_on={metric1_col:"sum", metric2_col:"sum"})
    data.fillna(0, inplace=True)
    data.sort_values(by=metric2_col, inplace=True)
    # Create Plotly Figure
    fig = go.Figure()

    # Add Metric 1 bars
    fig.add_trace(go.Bar(
        x=data[category_col],
        y=data[metric1_col],
        name=metric1_col,
        marker_color='deepskyblue'
    ))

    # Add Metric 2 bars
    fig.add_trace(go.Bar(
        x=data[category_col],
        y=data[metric2_col],
        name=metric2_col,
        marker_color='forestgreen'
    ))

    # Update layout for side-by-side bars
    fig.update_layout(
        barmode='group',
        title=chart_title,
        xaxis_title=category_col,
        yaxis_title="Values",
        legend_title="Metrics",
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def plot_day_vs_tod_heatmap(data, colorscale="RdYlGn_r", title = "Number of Accidents across Hour of the Day for Each Day of the Week"):
    data = group_and_aggregate(data, ["Day_of_Week", "Interval"], aggregate_on={"Number_of_Accidents":"sum"})
    # Define the correct order for days of the week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Convert the Day_of_Week column to a categorical type
    data['Day_of_Week'] = pd.Categorical(data['Day_of_Week'], categories=day_order, ordered=True)

    # Sort the data by Day_of_Week
    data = data.sort_values(by='Day_of_Week')
    pivot = data.pivot(index="Day_of_Week", columns="Interval", values="Number_of_Accidents")

    pivot.drop("-1 - 00", axis=1, inplace=True, errors="ignore")

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values, 
            x=[str(col) for col in pivot.columns],  # Force string labels
            y=pivot.index.to_list(), 
            colorscale=colorscale,
            colorbar=dict(title=f"{title}"),
            text=pivot.values,
            texttemplate="%{text:.0f}",
            textfont={"size":10}))

    fig.update_layout(
        # width=1200,  # Adjust width
        # height=500,  # Adjust height
        title=f'{title} Heatmap',
        xaxis_title='Hour of Day',
        yaxis_title='Day',
        font=dict(color="black") # Set the font color to black for better visibility
    )
    st.plotly_chart(fig)

def design_dashboard(data):

    display_initial_metrics(copy.deepcopy(data))
    st.write("---")
    st.write("## Trend Line for Accidents and Casualties Over Time")
    accident_vs_casualties(copy.deepcopy(data))
    st.write("---")
    st.write("## Distribution of Number of Accidents Over Dimensions")
    casualties_distributions(copy.deepcopy(data))
    st.write("---")
    st.write(f"## Comparison of Accidents and Casualties Across Different Dimensions")
    st.write(emoji.emojize(":bulb: Use the sidebar to filter data and explore distributions, such as accidents or casualties under specific road conditions, in fatal cases, or urban areas."))
    dimensions = {
        "Junction Control": "Junction_Control",
        "Junction Detail": "Junction_Detail",
        "Accident Severity": "Accident_Severity",
        "Light Conditions": "Light_Conditions",
        "Local Authority": "Local_Authority_(District)",
        "Carriageway Hazards": "Carriageway_Hazards",
        "Police Force": "Police_Force",
        "Road Surface Conditions": "Road_Surface_Conditions",
        "Road Type": "Road_Type",
        "Speed limit": "Speed_limit",
        "Area Type": "Urban_or_Rural_Area",
        "Weather Conditions": "Weather_Conditions",
        "Vehicle Type": "Vehicle_Type",
    }
    dimension = st.selectbox("Select a dimension", options=dimensions.keys())
    create_side_by_side_barchart(copy.deepcopy(data), dimensions[dimension], "Number_of_Accidents", "Number_of_Casualties")
    # map(copy.deepcopy(data))
    st.write("---")
    st.write("## Number of Accidents Distributed by Hour of the Day for Each Day of the Week")
    st.write(emoji.emojize(":bulb: Use the sidebar to filter data and find out critical hours requiring more surveillance."))
    plot_day_vs_tod_heatmap(copy.deepcopy(data))
