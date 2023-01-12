import streamlit as st
import pandas as pd

from utils.model import load_model
from utils.data_sources.etherscan import fetch_token_transfers, transfers_summary
from utils.data_sources.the_graph import fetch_swaps, uniswap_summary, \
    fetch_nft_trades, opensea_summary, opensea_account
from utils.helpers import combine_account_info
from utils.frontend.display import display_ml_prediction, display_uniswap, \
    display_opensea, display_token_transfers
from utils.frontend.images import ETH_IMG, ML_IMG, OPENSEA_IMG, SWAP_IMG, TOKEN_IMG

st.set_page_config(layout="wide",page_icon="🐤", page_title="Ethereum Account Profiling")

# Load ML model

model = load_model()

# Create Title

a, b = st.columns([1,9])
a.image(ETH_IMG, width=110)
b.title("ETHAP\nETHEREUM ACCOUNT PROFILING")

# Account input and data source selection

with st.form(key="search_form"):
    account = (st.text_input("Enter Account Identifier: ")).lower()

    a, b, c, d = st.columns([1, 1, 1, 3])

    swap = a.checkbox("Uniswap", True)
    opensea = b.checkbox("Opensea", True)
    token = c.checkbox("Transfers", True)
    search_button = st.form_submit_button(label="Search")

if account:
    with st.spinner(text='Querying data......'):
        if swap:
            uniswap_data = fetch_swaps(account)
        else:
            uniswap_data = pd.DataFrame()
        if opensea:
            opensea_data = fetch_nft_trades(account)
        else:
            opensea_data = pd.DataFrame()
        if token:
            transfers_data = fetch_token_transfers(account)
        else:
            transfers_data = pd.DataFrame()

        uniswap_dict = uniswap_summary(uniswap_data)
        opensea_dict = opensea_summary(opensea_data)
        transfers_dict = transfers_summary(transfers_data)

        X_pred = combine_account_info(opensea_dict, uniswap_dict, transfers_dict)

        if len(X_pred.dropna(how='all')) > 0:
            # ML Prediction

            profile = model.predict(X_pred)[0]
            a, b = st.columns([1, 20])
            a.image(ML_IMG, width=50)
            b.subheader('User profile')
            with st.expander('Machine Learning Model Prediction', expanded=True):
                display_ml_prediction(profile)

            # Uniswap

            a, b = st.columns([1, 20])
            a.image(SWAP_IMG, width=50)
            b.subheader('Uniswap transactions')
            with st.expander('Uniswap summary', expanded=True):
                if len(uniswap_data) > 0:
                    uniswap_history = uniswap_data[["amount", "date"]].set_index("date")
                    display_uniswap(uniswap_history, uniswap_dict)

                elif swap:
                    st.write("## There is no Uniswap transaction")

            with st.expander(':scroll: Uniswap dataframe', expanded=False):
                if len(uniswap_data) > 0:
                    st.dataframe(uniswap_data)

            # Opensea

            a, b = st.columns([1,20])
            a.image(OPENSEA_IMG, width=50)
            b.subheader('Opensea Transactions')
            with st.expander('Opensea summary', expanded=True):
                if len(opensea_data) > 0:
                    opensea_history = opensea_account(opensea_data)
                    display_opensea(opensea_history, opensea_dict)

                elif opensea:
                    st.write("## There is no Opensea transaction")

            with st.expander(':scroll: Opensea dataframe', expanded=False):
                if len(opensea_data) > 0:
                    st.dataframe(opensea_data)

            # Token transfers

            a, b = st.columns([1, 20])
            a.image(TOKEN_IMG, width=50)
            b.subheader('Token Transfers')
            with st.expander('Token transfer summary', expanded=True):
                if len(transfers_data) > 0:
                    display_token_transfers(transfers_data, transfers_dict)

                elif token:
                    st.write("## There is no token transfer")
            with st.expander(':scroll: Token transfer dataframe', expanded=False):
                if len(transfers_data) > 0:
                    st.dataframe(transfers_data)

        elif swap or opensea or token:
            st.write("## This account does not have any transactions")
