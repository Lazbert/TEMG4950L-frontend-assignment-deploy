import streamlit as st
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID, RANGE = st.secrets["sheet_secrets"]["spreadsheet_id"], st.secrets["sheet_secrets"]["range"]

@st.cache_resource()
def get_google_service():
    """
    Initialise Google service object to interact with Google Sheet API.
    
    Returns:
        service: Google service object to gain access to APIs
    """
    GCP_SERVICE_ACCOUNT = st.secrets["gcp_service_account"]
    SCOPES = st.secrets["sheet_secrets"]["service_account_scopes"]
    credentials = service_account.Credentials.from_service_account_info(
        GCP_SERVICE_ACCOUNT,
        scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)
    return service

# note queries are not cached if real-time update is the better case
def get_all_transactions(_sheets):  # since the spreadsheet object is not hashable, we can add an underscore (_) before the parameter
                                    # to tell streamlit it's not hashable
    """
    Retrieves all transactions in Google Sheet
    
    Paramters:
        _sheets: An object representing the spreadsheet in the Google Sheet database
    
    Returns:
        df_transactions (DataFrame): A dataframe containing all transaction records in the transaction tab of the spreadsheet
    """
    res = _sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
    header, transactions = res["values"][0], res["values"][1:]
    df_transactions = pd.DataFrame(transactions, columns=header).reindex(columns=["Date", "Symbol", "Action", "Amount of Crypto"])
    df_transactions["Amount of Crypto"] = df_transactions["Amount of Crypto"].astype(float)  # Google Sheet API will fetch number as string
    return df_transactions

def get_assets_composition(_sheets):
    """
    Retrieves net amount of each asset (cryptocurrency)
    
    Paramters:
        _sheets: An object representing the spreadsheet in the Google Sheet database
    
    Returns:
        df_assets_amount (DataFrame): A dataframe containing the net amount of each cryptocurrency (Buy - Sell)
    """
    res = _sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
    header, transactions = res["values"][0], res["values"][1:]
    df_assets_amount = pd.DataFrame(transactions, columns=header).reindex(columns=["Date", "Symbol", "Action", "Amount of Crypto"])
    df_assets_amount["Amount of Crypto"] = df_assets_amount["Amount of Crypto"].astype(float)
    
    # calculate net amount as of now: sum of all "Buy" - sum of all "Sell"
    buy_sell_multiplier = np.where(df_assets_amount["Action"] == "Buy", 1, -1)  # buy: positive; sell: negative
    df_assets_amount["Amount of Crypto"] = df_assets_amount["Amount of Crypto"] * buy_sell_multiplier
    df_assets_amount = df_assets_amount[["Symbol", "Amount of Crypto"]].groupby(by=["Symbol"]).sum()
    return df_assets_amount
