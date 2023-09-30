
import streamlit as st

SPREADSHEET_ID, RANGE = st.secrets["sheet_secrets"]["spreadsheet_id"], st.secrets["sheet_secrets"]["range"]

def upload_transaction(sheets, data: list):
    """
    Upload user inputs in the form as a transaction to the Google Sheet database.
    
    Parameters:
        data [list]: User inputs arranged as a list with the following order - [Date, Symbol, Action, Amound of Cypto]
    """
    sheets.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        insertDataOption="INSERT_ROWS",
        valueInputOption="USER_ENTERED",
        body={
            "values": [data]
        }
    ).execute()
    print("Uploaded following transaction successfully:")
    print(data)