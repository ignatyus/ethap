import requests
import streamlit as st
import pandas as pd
from utils.helpers import average_time

ETHERSCAN_URL = 'https://api.etherscan.io/api'
PK = st.secrets['etherscan_api']['KEY']

def fetch_token_transfers(account):
    query = f'{ETHERSCAN_URL}?module=account&action=tokentx&address={account}&page=1&startblock=0&sort=asc&apikey={PK}'
    response = requests.get(query)
    if response.status_code == 200 and isinstance(response.json()['result'], list):
        df = pd.DataFrame(response.json()['result'])
        if len(df) > 0:
            return clean_token_transfers(df, account)
    return pd.DataFrame()

def clean_token_transfers(df, account):
    df['account'] = account
    df['direction'] = ''
    df.loc[df['from'] == account, 'direction'] = 'sender'
    df.loc[df['to'] == account, 'direction'] = 'receiver'
    df['date'] = pd.to_datetime(df['timeStamp'], unit='s')
    df.drop(columns=['from', 'to', 'timeStamp'], inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def transfers_summary(df):
    if len(df) > 0:
        return {
            "n_sent": len(df[df["direction"] == "sender"]),
            "n_received": len(df[df["direction"] == "receiver"]),
            "nunique_tokens": df["contractAddress"].nunique(),
            "avg_time_transfers": average_time(df["date"])
        }
    else:
        return {
            "n_sent": None,
            "n_received": None,
            "nunique_tokens": None,
            "avg_time_transfers": None
        }
