import streamlit as st
from datetime import datetime
import plotly.express as px
from api.queries import get_google_service, get_all_transactions, get_assets_composition
from api.mutations import upload_transaction

# My Portfolio Page goes here
service = get_google_service()
sheets = service.spreadsheets()

def validate_order():
    """
    Checks whether all 4 fields in the form are entered and if the date is valid.
    Uploads the order to Google Sheet if there are no errors.
    """
    crypto_code = st.session_state.crypto_code
    transaction_date = st.session_state.transaction_date
    action = st.session_state.action
    amount = st.session_state.amount
    print(crypto_code, transaction_date, action, amount)
    
    # validate inputs - all should be required fields
    error_flag = False
    if crypto_code is None:
        st.sidebar.warning("Please provide a cryptocurrency.", icon="⚠️")
        error_flag = True
    if amount is None:
        st.sidebar.warning("Please specify the amount of cryptocurrency.", icon="⚠️")
        error_flag = True
    if transaction_date is None:
        st.sidebar.warning("Please provide a date.", icon="⚠️")
        error_flag = True

    # check if date is valid
    if transaction_date < datetime.now().date():
        st.sidebar.warning("Please select a date in the future.", icon="⚠️")
        error_flag = True
    
    if not error_flag:
        transaction_date = transaction_date.strftime(r"%d/%m/%Y")
        data = [str(transaction_date), crypto_code, action, amount]  # date, symbol, action, amount of crypto
        upload_transaction(sheets, data)

df_transactions = get_all_transactions(sheets)
df_assets_amount = get_assets_composition(sheets)
df_assets_amount = df_assets_amount.rename(columns={"Amount of Crypto": "Unit of Crypto"})
fig = px.bar(df_assets_amount,
             labels={
                 "Symbol": "Cryptocurrency",
                 "value": "Unit of Cryptocurrency"
             },
             color="value",
             color_continuous_scale=px.colors.sequential.Oryel,
             text_auto=True,
             height=500)
fig.update_layout(bargap=0.5)

# === Widgets === 
st.title("My Portfolio")

# form for data entry
st.sidebar.title("Make an Order")
with st.sidebar.form("new_transaction", clear_on_submit=True):
    crypto_code = st.selectbox("Cryptocurrency Code",
                               index=None,
                               placeholder="Select a cryptocurrency",
                               options=["AAVE", "BNB","BTC", "ADA", "LINK", "ATOM", "CRO", "DOGE", "EOS", "ETH", "MIOTA", "LTC", "XMR", "XEM", "DOT", "SOL", "XLM", "USDT", "TRX", "UNI", "USDC", "WBTC", "XRP"],
                               key="crypto_code")
    
    transaction_date = st.date_input("Date of Transaction", value=datetime.now(), key="transaction_date")
    action = st.selectbox("Action", options=["Buy", "Sell"], key="action")
    amount = st.number_input("Amount", placeholder="Please provide a number", value=None, step=1e-5, format="%.5f", key="amount")
    submitted = st.form_submit_button("Execute", type="primary", on_click=validate_order)
    
# asset composition + indicators
st.subheader("Your assets")
col1, _ = st.columns([3, 2])
col1.plotly_chart(fig, use_container_width=True)

# table for transaction history
st.subheader("Transaction History")
st.dataframe(df_transactions, use_container_width=True, hide_index=True)