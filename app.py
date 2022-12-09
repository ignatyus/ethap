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

a, b = st.columns(2)

with a:
    st.text("")
    st.image("https://ethereum.org/static/c48a5f760c34dfadcf05a208dab137cc/3a0ba/eth-diamond-rainbow.webp", width=100)
with b:
    st.title("   ETHAP   \n ETHEREUM ACCOUNT PROFILING")

list_selctions = ['NFT', 'UNISWAP','Token Transfer']
# Request data entry for account selection

try:
    account = st.text_input("Enter Account Identifier: ")

except:
    st.error("Please make sure you enter a valid account")
    st.stop()

model = load_model(st.secrets["mlflow_params"])

if account:
    with st.spinner(text='Querying data......'):

        uniswap_data = fetch_swaps(account, 1000, starting_ts='0', trial=100)
        uniswap_dict = uniswap_summary(uniswap_data)
        opensea_data = fetch_nft_trades(account, limit = 1000)
        opensea_dict = opensea_summary(opensea_data)
        transfers_data = fetch_parse_public_tansaction(table="token_transfers", account = account, limit = 1000, secrets=st.secrets["gcp_service_account"])
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
        if len(X_pred.dropna()) > 0:
            display_dial('Predicted group:', str(model.predict(X_pred)), COLOR_PINK)

            if len(uniswap_data) > 0:
                st.subheader('Uniswap Transactions')
                a, b, c, d = st.columns(4)
                with a:
                    display_dial("Number of swaps", f"{uniswap_dict['n_swaps']}", COLOR_BLUE)
                with b:
                    display_dial("Number of pools interacted with",  f"{uniswap_dict['nunique_pools']}", COLOR_PINK)
                with c:
                    display_dial("Average swap volume ($)", f"{uniswap_dict['avg_swap_volume']}", COLOR_CYAN)
                with d:
                    display_dial("Average time between swaps",  str(timedelta(seconds=uniswap_dict['avg_time_swaps'].round())), COLOR_PINK)

                uniswap_amount = uniswap_account(uniswap_data)
                hist_data = uniswap_amount.index
                group_labels = uniswap_amount["amount"]
                time_gap = uniswap_amount.index[-1]-uniswap_amount.index[0]
                #n_bins = len(uniswap_amount)/time_gap.days
                data_div = 30
                n_bins = int(len(uniswap_amount) / data_div)
                plot=px.histogram(group_labels, hist_data, histfunc = 'sum', nbins = 10)

                plot.update_layout(title_text="Timeseries Transactions",bargap=0.025)
                plot.update_traces(marker=dict(color="#de21ce"))
                plot.update_yaxes(title_text='amount total',type='log')
                st.plotly_chart(plot)


            else:
                st.write("There is no Uniswap transaction")


            if len(opensea_data) > 0:
                st.subheader('Opensea Transactions')
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


                opensea_amount = opensea_account(opensea_data)
                hist_data = opensea_amount.index
                group_labels = opensea_amount["amount"]        # name of the dataset
                time_gap = opensea_amount.index[-1]-opensea_amount.index[0]
                #n_bins = len(opensea_amount)/time_gap.days
                data_div = 30
                n_bins = int(len(opensea_amount) / data_div)
                plot=px.histogram(group_labels, hist_data, histfunc = 'sum', nbins = 10)

                plot.update_layout(title_text="Timeseries Transactions",bargap=0.025)
                plot.update_traces(marker=dict(color="#de21ce"))
                plot.update_yaxes(title_text='amount total',type='log')
                st.plotly_chart(plot)

            else:
                st.write("There is no Opensea transaction")


            if len(transfers_data) > 0:
                st.subheader('Token Transfers')
                a, b, c, d = st.columns(4)
                with a:
                    display_dial("Number of withdrawals", f"{transfers_dict['n_sent']}", COLOR_BLUE)
                with b:
                    display_dial("Number of deposits",  f"{transfers_dict['n_received']}", COLOR_PINK)
                with c:
                    display_dial("Number of tokens interacted with", f"{transfers_dict['nunique_tokens']}", COLOR_CYAN)
                with d:
                    display_dial("Average time between transfers",  str(timedelta(seconds=transfers_dict['avg_time_transfers'].round())), COLOR_PINK)

            else:
                st.write("There is no token transfer")
        else:
            st.write("This account does not have any transactions")
