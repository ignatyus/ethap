import streamlit as st
import numpy as np
import matplotlib as plt
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
import plotly.express as px
from datetime import timedelta
from ETHAP.utils.data import (
    uniswap_summary, opensea_summary, opensea_account, transfers_summary,
    fetch_nft_trades, fetch_parse_public_tansaction, fetch_swaps,
    uniswap_account, load_model
)
st.set_page_config(layout="wide",page_icon="🐤", page_title="Ethereum Account Profiling")

ETH_IMG = "https://ethereum.org/static/c48a5f760c34dfadcf05a208dab137cc/3a0ba/eth-diamond-rainbow.webp"
OPENSEA_IMG ="https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/OpenSea_icon.svg/2048px-OpenSea_icon.svg.png"
SWAP_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Uniswap_Logo.svg/1026px-Uniswap_Logo.svg.png"
TOKEN_IMG = "https://cdn-icons-png.flaticon.com/512/1372/1372789.png"

# from ETHAP.utils.get_data import get_uniswap_data

COLOR_RED   = "#FF4B4B"
COLOR_BLUE  = "#1C83E1"
COLOR_CYAN  = "#00C0F2"
COLOR_GREEN = "#4feb34"
COLOR_PINK  = "#de21ce"

def display_dial(title, value, color):
        st.markdown(
            div(
                style=styles(
                    text_align="center",
                    color=color,
                    padding=(rem(0.8), 0, rem(3), 0),
                )
            )(
                h2(style=styles(font_size=rem(0.8), font_weight=600, padding=0))(title),
                big(style=styles(font_size=rem(1.5), font_weight=800, line_height=1))(
                    value
                ),
            ),
            unsafe_allow_html=True,
        )

# Creating Title Page

a, b = st.columns([1,8])
with a:
    st.image(ETH_IMG, width=80)
with b:
    st.title("ETHAP\nETHEREUM ACCOUNT PROFILING")

list_selctions = ['NFT', 'UNISWAP','Token Transfer']
# Request data entry for account selection

with st.form(key="search_form"):
    try:
        account = (st.text_input("Enter Account Identifier: ")).lower()

    except:
        st.error("Please make sure you enter a valid account")
        st.stop()
    a, b, c, d = st.columns([1, 1, 1, 3])

    swap = a.checkbox("Uniswap", True)
    opensea = b.checkbox("Opensea", True)
    token = c.checkbox("Transfers", True)
    search_button = st.form_submit_button(label="Search")

model = load_model(st.secrets["mlflow_params"])

if account:
    with st.spinner(text='Querying data......'):
        if swap:
            uniswap_data = fetch_swaps(account, 1000, starting_ts='0', trial=100)
        else:
            uniswap_data = pd.DataFrame()
        if opensea:
            opensea_data = fetch_nft_trades(account, limit = 1000)
        else:
            opensea_data = pd.DataFrame()
        if token:
            transfers_data = fetch_parse_public_tansaction(table="token_transfers", account = account, limit = 1000, secrets=st.secrets["gcp_service_account"])
        else:
            transfers_data = pd.DataFrame()

        uniswap_dict = uniswap_summary(uniswap_data)
        opensea_dict = opensea_summary(opensea_data)
        transfers_dict = transfers_summary(transfers_data)

        X_pred = pd.DataFrame(dict(
            n_sells=[opensea_dict['n_sells']],
            sell_volume=[opensea_dict['sell_volume']],
            n_buys=[opensea_dict['n_buys']],
            buy_volume=[opensea_dict['buy_volume']],
            nunique_collections=[opensea_dict['nunique_collections']],
            avg_time_trades=[opensea_dict['avg_time_trades']],
            n_swaps=[uniswap_dict['n_swaps']],
            nunique_pools=[uniswap_dict['nunique_pools']],
            avg_swap_volume=[uniswap_dict['avg_swap_volume']],
            avg_time_swaps=[uniswap_dict['avg_time_swaps']],
            n_sent=[transfers_dict['n_sent']],
            n_received=[transfers_dict['n_received']],
            nunique_tokens=[transfers_dict['nunique_tokens']],
            avg_time_transfers=[transfers_dict['avg_time_transfers']]))

        if len(X_pred.dropna(how='all')) > 0:
            profile = model.predict(X_pred)[0]
            if profile == 5:
                display_dial('Predicted group:', 'High frequency, mid volume NFT trader', COLOR_PINK)
            elif profile == 6:
                display_dial('Predicted group:', 'High volume, mid frequency NFT trader', COLOR_PINK)
            elif profile == 7:
                display_dial('Predicted group:', 'High frequency cryptocurrency trader', COLOR_PINK)
            else:
                display_dial('Predicted group:', str(profile), COLOR_PINK)

            if len(uniswap_data) > 0:
                a, b = st.columns([1, 20])
                with a:
                    st.image(SWAP_IMG, width=60)
                with b:
                    st.subheader('Uniswap transactions')
                with st.expander('Uniswap summary', expanded=True):
                    uniswap_amount = uniswap_account(uniswap_data)
                    st.write("##### Fetched ", len(uniswap_amount)," transactions from uniswap source...")
                    a, b, c, d = st.columns(4)
                    with a:
                        display_dial("Number of swaps", f"{uniswap_dict['n_swaps']}", COLOR_BLUE)
                    with b:
                        display_dial("Number of pools interacted with",  f"{uniswap_dict['nunique_pools']}", COLOR_PINK)
                    with c:
                        display_dial("Average swap volume ($)", f"{uniswap_dict['avg_swap_volume']}", COLOR_CYAN)
                    with d:
                        display_dial("Average time between swaps",  str(timedelta(seconds=uniswap_dict['avg_time_swaps'].round())), COLOR_PINK)

                    st.write(" \n")
                    st.write(" \n")

                    st.write("###### Swap History")
                    st.bar_chart(uniswap_amount)
                with st.expander(':scroll:Uniswap dataframe', expanded=False):
                    st.dataframe(uniswap_data)

            elif swap:
                st.write("There is no Uniswap transaction")

            if len(opensea_data) > 0:
                a, b = st.columns([1,20])
                with a:
                    st.image(OPENSEA_IMG, width=45)
                with b:
                    st.subheader('Opensea Transactions')
                with st.expander('Opensea summary', expanded=True):
                    opensea_amount = opensea_account(opensea_data)
                    st.write("##### Fetched ", len(opensea_amount)," transactions from opensea source...")
                    a, b, c, d, e, f = st.columns(6)
                    with a:
                        display_dial("Number of NFT buys",  f"{opensea_dict['n_buys']}", COLOR_PINK)
                    with b:
                        display_dial("Number of NFT sells", f"{opensea_dict['n_sells']}", COLOR_CYAN)
                    with c:
                        display_dial("Buy volume (ETH)",  f"{opensea_dict['buy_volume']}", COLOR_PINK)
                    with d:
                        display_dial("Sell volume (ETH)",  f"{opensea_dict['sell_volume']}", COLOR_CYAN)
                    with e:
                        display_dial("Number of unique collections interacted with",  f"{opensea_dict['nunique_collections']}", COLOR_CYAN)
                    with f:
                        display_dial("Average time between NFT trades", str(timedelta(seconds=opensea_dict['avg_time_trades'].round())), COLOR_BLUE)



                    st.write(" \n")
                    st.write(" \n")

                    a, b = st.columns([1,0.6])
                    with a:
                        st.write("###### NFT Trade History")
                        st.bar_chart(opensea_amount, height=480)
                    with b:
                        st.write("###### Buy vs. Sell")
                        fig = go.Figure(data=[go.Pie(labels=["buy volume", "sell volume"],
                                                    values=([opensea_dict["buy_volume"], opensea_dict["sell_volume"]]))])
                        st.plotly_chart(fig, use_container_width=True)
                with st.expander(':scroll:Opensea dataframe', expanded=False):
                    st.dataframe(opensea_data)

            elif opensea:
                st.write("There is no Opensea transaction")

            if len(transfers_data) > 0:
                a, b = st.columns([1, 20])
                with a:
                    st.image(TOKEN_IMG, width=70)
                with b:
                    st.subheader('Token Transfers')
                with st.expander('Token transfer summary', expanded=True):
                    st.write("##### Fetched ", len(transfers_data)," transactions from token transfers source...")
                    a, b, c, d = st.columns(4)
                    with a:
                        display_dial("Number of withdrawals", f"{transfers_dict['n_sent']}", COLOR_BLUE)
                    with b:
                        display_dial("Number of deposits",  f"{transfers_dict['n_received']}", COLOR_PINK)
                    with c:
                        display_dial("Number of tokens interacted with", f"{transfers_dict['nunique_tokens']}", COLOR_CYAN)
                    with d:
                        display_dial("Average time between transfers",  str(timedelta(seconds=transfers_dict['avg_time_transfers'].round())), COLOR_PINK)
                with st.expander(':scroll:Token transfer dataframe', expanded=False):
                    st.dataframe(transfers_data)
            elif token:
                st.write("There is no token transfer")
        elif swap or opensea or token:
            st.write("This account does not have any transactions")
