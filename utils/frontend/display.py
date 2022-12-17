import streamlit as st
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
from datetime import timedelta
import plotly.graph_objects as go

from utils.frontend.colors import COLOR_BLUE, COLOR_CYAN, COLOR_PINK

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

def display_ml_prediction(profile):
    if profile == 0:
        display_dial('Account profile:', 'Junior NFT Explorer', COLOR_PINK)
        st.write('''### High frequency, low volume NFT trader.  \n
                 Likes to explore new collections.''')
    elif profile == 1:
        display_dial('Account profile:', 'Infrequent account', COLOR_PINK)
        st.write('### Does not have many transactions.')
    elif profile == 2:
        display_dial('Account profile:', 'Junior Cryptocurrency Trader', COLOR_PINK)
        st.write('### Mid volume cryptocurrency trader.')
    elif profile == 3:
        display_dial('Account profile:', 'Common account', COLOR_PINK)
        st.write('### Does not have that much activity on dApps.')
    elif profile == 5:
        display_dial('Account profile:', 'Senior NFT Explorer', COLOR_PINK)
        st.write('''### High frequency, mid volume NFT trader.  \n
                 Likes to explore new collections.''')
    elif profile == 6:
        display_dial('Account profile:', 'NFT Whale', COLOR_PINK)
        st.write('''### High volume, mid frequency NFT trader.  \n
                 Likes to trade expensive NFTs.''')
    elif profile == 7:
        display_dial('Account profile:', 'Senior Cryptocurrency Trader', COLOR_PINK)
        st.write('''### Mid volume cryptocurrency trader.  \n
                 Frequent user, does a lot of token transfers.''')
    else:
        display_dial('Account profile:', 'Category not analyzed', COLOR_PINK)
        st.write('''### The behavior of this account type will be analyzed soon...
                 Our model's prediction needs to be analyzed before we can give a descriptive label to this account.''')

    st.write('''Disclaimer: This prediction is made by an unsupervised clustering ML model.
                It has trained on over 100k accounts, looking through hundreds of millions of transactions.
                However, our model could be more advanced and needs more training.''')

def display_uniswap(uniswap_history, uniswap_dict):
    st.write("##### Fetched ", len(uniswap_history)," transactions from Uniswap v3...")
    a, b, c, d = st.columns(4)
    with a:
        display_dial("Number of swaps", f"{uniswap_dict['n_swaps']}", COLOR_BLUE)
    with b:
        display_dial("Number of pools interacted with",  f"{uniswap_dict['nunique_pools']}", COLOR_PINK)
    with c:
        display_dial("Average swap volume ($)", f"{uniswap_dict['avg_swap_volume']}", COLOR_CYAN)
    with d:
        if uniswap_dict['avg_time_swaps']:
            time = str(timedelta(seconds=uniswap_dict['avg_time_swaps']))
        else:
            time = '-'
        display_dial("Average time between swaps",  time, COLOR_PINK)

    st.write(" \n")
    st.write(" \n")

    st.write("###### Swap History")
    st.bar_chart(uniswap_history)

def display_opensea(opensea_history, opensea_dict):
    st.write("##### Fetched ", len(opensea_history)," transactions from Opensea Seaport...")
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
        display_dial("Number of unique collections interacted with", f"{opensea_dict['nunique_collections']}", COLOR_CYAN)
    with f:
        if opensea_dict['avg_time_trades']:
            time = str(timedelta(seconds=opensea_dict['avg_time_trades']))
        else:
            time = '-'
        display_dial("Average time between NFT trades", time, COLOR_BLUE)

    st.write(" \n")
    st.write(" \n")

    a, b = st.columns([1,0.6])
    with a:
        st.write("###### NFT Trade History")
        st.bar_chart(opensea_history, height=480)
    with b:
        st.write("###### Buy vs. Sell")
        fig = go.Figure(
            data=[go.Pie(labels=["buy volume", "sell volume"],
            values=([opensea_dict["buy_volume"], opensea_dict["sell_volume"]]))]
        )
        st.plotly_chart(fig, use_container_width=True)

def display_token_transfers(transfers_data, transfers_dict):
    st.write("##### Fetched ", len(transfers_data)," token transfers...")
    a, b, c, d = st.columns(4)
    with a:
        display_dial("Number of withdrawals", f"{transfers_dict['n_sent']}", COLOR_BLUE)
    with b:
        display_dial("Number of deposits",  f"{transfers_dict['n_received']}", COLOR_PINK)
    with c:
        display_dial("Number of tokens interacted with", f"{transfers_dict['nunique_tokens']}", COLOR_CYAN)
    with d:
        if transfers_dict['avg_time_transfers']:
            time = str(timedelta(seconds=transfers_dict['avg_time_transfers']))
        else:
            time = '-'
            display_dial("Average time between transfers",  time, COLOR_PINK)
