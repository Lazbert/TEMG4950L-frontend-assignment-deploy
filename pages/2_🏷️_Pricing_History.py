import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import re

DATA_DIR = "./assets/data"  # relative to the ROOT directory, not the one of the current file
DEFAULT_CRYPTO = ["Bitcoin", "Ethereum", "Litecoin", "Uniswap", "Dogecoin"]

# Pricing History page goes here
st.set_page_config("Pricing History", page_icon="./assets/icons/IconDashboard.png", layout="wide")

# load 5 cryptocurrency data: Bitcoin, Ethereum, Litecoin, Uniswap, and Dogecoin by default
@st.cache_data  # this decorator prevents running this function with the same parameter (name) on each render, i.e the dataframes will be cached
def load_crypto_data(name: str):
    """
    Loads specified static cryptocurrency data in the ../assets/data folder as a dataframe.
    Then processes the dataframe by daily, quarterly, and yearly, where the data is averaged over the interval to obtain each data point.
    
    Parameters:
        name (str): symbol of a cryptocurrency, e.g BTC, ETH
    
    Returns:
        packed_df (dict[str, DataFrame]): dictionary of string intervals and the corresponding dataframes
    """
    csv_name = f"coin_{name}.csv"
    print(f"Reading {csv_name} data")
    if csv_name in os.listdir(DATA_DIR):
        df = pd.read_csv(f"{DATA_DIR}/{csv_name}", index_col="SNo")
        
        # process date column, note the given data is in daily interval
        df["Date"] = pd.to_datetime(df["Date"])
        df["Daily"] = df["Date"].apply(lambda dt: dt.strftime(r"%Y-%m-%d"))
        
        df["Quarterly"] = df["Date"].apply(lambda dt: f"{dt.year} Q{dt.quarter}")
        df["Yearly"] = df["Date"].apply(lambda dt: f"{dt.year}")
        df_quarterly = df[["Quarterly", "High", "Low", "Open", "Close", "Volume", "Marketcap"]].groupby(by=["Quarterly"], as_index=False).mean()
        df_yearly = df[["Yearly", "High", "Low", "Open", "Close", "Volume", "Marketcap"]].groupby(by=["Yearly"], as_index=False).mean()
        
        print(f"\u2714 Successfully read and processed {csv_name} with {df.shape[0]} rows")
        
        packed_df = {
            "Daily": df,
            "Quarterly": df_quarterly,
            "Yearly": df_yearly
        }
        
        return packed_df 
    
    else:
        print(f"\u274c Unable to find data for the cryptocurrency: {name}")

def get_crypto_plot(selected_crypto: list[str], time_frame: str, tab: str="High"):
    """
    Initialise and plot a figure and add a line plot for each cryptocurrency selected in the sidebar.
    Shows data matching the selected tab above the figure.
    
    Paramters:
        selected_crypto (list[str]): Maximum of 5 cryptocurrencies' symbols selected in the sidebar
        time_frame (str): Time interval of how the figure is displayed selected in the slider.
        tab (str): Specifies which data should be shown. Either one of: High, Low, Open, Close, Volume, Market Capitalisation
    """
    crypto_dfs = { name: load_crypto_data(name) for name in selected_crypto }
    fig = go.Figure()
    for crypto, time_dfs in crypto_dfs.items():
        crypto_df = time_dfs[time_frame]
        date_x_axis = crypto_df[time_frame]
        fig = fig.add_trace(go.Line(x=date_x_axis, y=crypto_df[tab], name=crypto))  # adding suplots to create a multi-series graph
    
    st.plotly_chart(fig, use_container_width=True)

# === Widgets ===
st.title("Pricing History")

# sidebar
st.sidebar.title("Filter Criteria")
st.sidebar.header("Cryptocurrency")
selected_crypto = st.sidebar.multiselect(
    "Please select at max 5 cryptocurrencies here:",
    options=[re.match(r"coin_(.*).csv", csv_data)[1] for csv_data in os.listdir(DATA_DIR)],
    default=DEFAULT_CRYPTO,
    max_selections=5
)

# time options
st.subheader("Select a time interval you wish the data to be displayed in:", )
_, col, _ = st.columns([1, 5, 5]) 
time_frame = col.select_slider(
    "",
    options=["Daily", "Quarterly", "Yearly"],
)

# graph
high, low, open, close, volume, market_cap = st.tabs(["High", "Low", "Open", "Close", "Volume", "Market Capitalisation"])
with high:
    get_crypto_plot(selected_crypto, time_frame)
with low:
    get_crypto_plot(selected_crypto, time_frame, "Low")
with open:
    get_crypto_plot(selected_crypto, time_frame, "Open")
with close:
    get_crypto_plot(selected_crypto, time_frame, "Close")
with volume:
    get_crypto_plot(selected_crypto, time_frame, "Volume")
with market_cap:
    get_crypto_plot(selected_crypto, time_frame, "Marketcap")