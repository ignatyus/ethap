import streamlit as st
import numpy as np
import matplotlib as plt
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
import plotly.express as px
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

c, d, e = st.columns(3)
st.sidebar.image("https://ethereum.org/static/0feeac3f7182fbfa52ee3aa146840325/b5b69/wallet.webp", width=300)


with a:
    st.text("")
    st.image("https://ethereum.org/static/c48a5f760c34dfadcf05a208dab137cc/3a0ba/eth-diamond-rainbow.webp", width=100)
with b:
    st.title("- ETHAP - \n ETHEREUM ACCOUNT PROFILING")

list_selctions = ['NFT', 'UNISWAP','Token Transfer']
# Request data entry for account selection

try:
    a,b = st.columns([1,1])

    account = b.text_input("Enter Account Identifier: ")
    limit_param = a.slider("Trade limit", 1, 1000, 100)

except:
    st.error("Please make sure you enter a valid account")
    st.stop()

model = load_model(st.secrets["mlflow_params"])

#colour assigmnet
average_time_colour = COLOR_BLUE
n_buys_colour = COLOR_PINK
n_sells_colour = COLOR_CYAN
total_buys_colour = COLOR_PINK
total_sells_colour = COLOR_CYAN


opensea_data = fetch_nft_trades(account, limit = limit_param)
opensea_dict = opensea_summary(opensea_data)
if len(opensea_data) > 0:
    st.subheader('Opensea Transactions')
    a, b, c, d , e, f = st.columns(6)
    with a:
        display_dial("average time in s", f"{opensea_dict['avg_time_trades']}", average_time_colour)
    with b:
        display_dial("number buys",  f"{opensea_dict['n_buys']}", n_buys_colour)
    with c:
        display_dial("number sells", f"{opensea_dict['n_sells']}", n_sells_colour)
    with d:
        display_dial("volume buys ETH",  f"{opensea_dict['buy_volume']}", total_buys_colour)
    with e:
        display_dial("volume sells ETH",  f"{opensea_dict['sell_volume']}", total_sells_colour)
    with f:
        display_dial("nunique_collections",  f"{opensea_dict['nunique_collections']}", total_sells_colour)
else:
    st.write("There is no Opensea transaction")

transfers_data = fetch_parse_public_tansaction(table="token_transfers", account = account, limit = 1000, secrets=st.secrets["gcp_service_account"])
transfers_dict = transfers_summary(transfers_data)
if len(transfers_data) > 0:
    st.subheader('Token Transfers')
    a, b, c, d = st.columns(4)
    with a:
        display_dial("n_sent", f"{transfers_dict['n_sent']:.2f}", average_time_colour)
    with b:
        display_dial("n_received",  f"{transfers_dict['n_received']}", n_buys_colour)
    with c:
        display_dial("nunique_tokens", f"{transfers_dict['nunique_tokens']}", n_sells_colour)
    with d:
        display_dial("avg_time_transfers",  f"{transfers_dict['avg_time_transfers']}", total_buys_colour)

else:
    st.write("There is no token transfer")

uniswap_data = fetch_swaps(account, limit_param, starting_ts='0', trial=100)
uniswap_dict = uniswap_summary(uniswap_data)
if len(uniswap_data) > 0:
    st.subheader('Uniswap transactions')
    a, b, c, d = st.columns(4)
    with a:
        display_dial("n_swaps", f"{uniswap_dict['n_swaps']:.2f}", average_time_colour)
    with b:
        display_dial("nunique_pools",  f"{uniswap_dict['nunique_pools']}", n_buys_colour)
    with c:
        display_dial("avg_swap_volume", f"{uniswap_dict['avg_swap_volume']}", n_sells_colour)
    with d:
        display_dial("avg_time_swaps",  f"{uniswap_dict['avg_time_swaps']}", total_buys_colour)

else:
    st.write("There is no Uniswap transaction")

if account:
    combined_dict = opensea_dict | uniswap_dict | transfers_dict
    for key, value in combined_dict.items():
        combined_dict[key] = [value]
    df = pd.DataFrame(combined_dict)
    display_dial('Predicted group:', str(model.predict(df)), COLOR_PINK)


# Scatter plot on swap and opensea

fig = make_subplots(rows=1, cols=2, subplot_titles=("Uniswap", "Opensea"))
if len(uniswap_data) >0:
    swap_amount = uniswap_account(uniswap_data)
    fig.add_trace(go.Scatter(x=swap_amount.index,
                         y=swap_amount["amount"],
                         mode="markers",
                         name="transaction"
                         ),
               row=1, col=1)

if len(opensea_data) > 0:
    opensea_amount = opensea_account(opensea_data)
    fig.add_trace(go.Scatter(x=opensea_amount.index,
                         y=opensea_amount["amount"],
                         mode="markers",
                         name="transaction"
                         ),
               row=1, col=2)

fig.update_layout(title_text="Subplots with Annotations")

st.plotly_chart(fig)

if len(opensea_data) >0:
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

if len(uniswap_data) >0:
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
