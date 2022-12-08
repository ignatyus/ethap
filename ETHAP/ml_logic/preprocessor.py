import pandas as pd
import numpy as np

#average
def average_time(account: pd.Series):
    account.sort_values(inplace=True)
    return (account - account.shift(1)).dt.total_seconds().mean()

#total buy amount
def buy_volume(buy: pd.Series):
    return buy[buy['total_amount'] > 0].sum()

#total sell amount
def sell_volume(sell: pd.Series):
    return sell[sell['total_amount'] < 0].sum()

#number of seller
def n_sell(sd: pd.Series):
    return sd[sd=="sell"].count()

#number of buyer
def n_buy(sd: pd.Series):
    return sd[sd=="buy"].count()

def feature_engineer(df:pd.DataFrame):
    # remove buggy transactions
    df = df.drop_duplicates()
    df = df.dropna(how="any", axis=0)

    # remove transactions that have no value
    df = df[(df['amount'] != 0) | (df['priceETH'] != 0)]

    df["total_amount"] = df["amount"] * df["priceETH"]

    df['date'] = pd.to_datetime(df['timestamp'], unit='s')

    df_1 = df.copy()
    df_2 = df.copy()

    df_1.rename(columns={"seller": "from"}, inplace=True)
    df_2.rename(columns={"buyer": "from"}, inplace=True)

    df_1['total_amount'] = df_1['total_price']
    df_2['total_amount'] = - df_2['total_price']
    df_1["buy_or_sell"]='sell'
    df_2["buy_or_sell"]='buy'
    combined_df = pd.concat([df_1, df_2])

    processed = combined_df.groupby("from", as_index=False)[[
        'from', 'date', 'total_amount', 'buy_or_sell','collectionId'
    ]].aggregate({
        'buy_or_sell': [n_sell, n_buy],
        'total_amount' : [sell_volume, buy_volume],
        'date': average_time,
        'collectionId': 'nunique'
    })

    return processed
