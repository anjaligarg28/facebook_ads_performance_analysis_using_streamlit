import pandas as pd
import os
import streamlit as st

from utils.dashboard import design_sidebar

st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(
    page_title="Road Accident Data Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# Add custom CSS to adjust sidebar width
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 0px;  /* Adjust the minimum width */
        max-width: 280px;  /* Adjust the maximum width */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def main():

    filepath = os.path.join(os.getcwd(), "data", "compressed_data.csv.gz")
    data = pd.read_csv(filepath)
    design_sidebar(data)

if __name__=="__main__":
    main()


