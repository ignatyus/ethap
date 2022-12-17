import pandas as pd
import requests
from utils.helpers import average_time

UNISWAP_URL = 'https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-ethereum'
OPENSEA_URL = 'https://api.thegraph.com/subgraphs/name/messari/opensea-seaport-ethereum'

### Post Query to the Graph Network ###

def post_query(url, query, trial):
    for i in range(trial):
        response = requests.post(url, '', json={'query':query})
        if response.status_code == 200 and 'data' in response.json():
            return response.json()

### Uniswap ###

def parse_swaps(swaps):
    for swap in swaps:
        swap['protocolId'] = swap['protocol']['id']
        del swap['protocol']
        swap['tokenInId'] = swap['tokenIn']['id']
        del swap['tokenIn']
        swap['tokenOutId'] = swap['tokenOut']['id']
        del swap['tokenOut']
        swap['poolId'] = swap['pool']['id']
        del swap['pool']
    return swaps

def fetch_swaps(account, limit=1000, starting_ts='0', trial=100):
    query = '''{
        swaps (first: %i,
            orderBy: timestamp,
            orderDirection: desc,
            where: {
                timestamp_gt: %s,
                from: %s
            }) {
            id,
            hash,
            logIndex,
            protocol { id },
            to,
            from,
            blockNumber,
            timestamp,
            tokenIn { id },
            amountIn,
            amountInUSD,
            tokenOut { id },
            amountOut,
            amountOutUSD,
            pool { id }
        }
    }'''

    swaps = post_query(
        UNISWAP_URL,
        query %(limit, starting_ts, f'"{account}"'),
        trial=trial
    )['data']['swaps']
    swaps_df = pd.DataFrame(parse_swaps(swaps))

    if len(swaps_df) > 0:
        return clean_swaps(swaps_df)

    return swaps_df

def clean_swaps(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    df.sort_values("date", inplace=True)

    # Group the transactions by the hash to remove hashes that has more than 1 transaction
    txs = df.groupby(by="hash").count()[["from"]]
    txs = txs.loc[txs["from"] == 1].index
    df = df[df["hash"].isin(txs)]

    df = df.drop_duplicates()
    df = df.dropna(how="any", axis=0)
    df[["amountInUSD", "amountOutUSD"]] = df[["amountInUSD", "amountOutUSD"]].astype("float")

    # remove transactions that have no value
    df = df[(df['amountInUSD'] != 0) | (df['amountOutUSD'] != 0)]

    # Fill the transaction amount if one of the values is available
    tmp = df[df['amountInUSD'] == 0]['amountOutUSD']
    df.loc[tmp.index, 'amountInUSD'] = tmp
    tmp = df[df['amountOutUSD'] == 0]['amountInUSD']
    df.loc[tmp.index, 'amountOutUSD'] = tmp


    # Represent the amount as the mean(amountInUSD, amountOutUSD)
    df["amount"] = (df["amountInUSD"] + df["amountOutUSD"]) / 2
    return df

def uniswap_summary(df: pd.DataFrame):
    if len(df) > 0:
        return {
            "n_swaps":         df["hash"].count(),
            "nunique_pools":   df['poolId'].nunique(),
            "avg_swap_volume": df["amount"].mean().round(2),
            "avg_time_swaps":  average_time(df["date"])
        }
    else:
        return {
            "n_swaps":         None,
            "nunique_pools":   None,
            "avg_swap_volume": None,
            "avg_time_swaps":  None
        }



### Opensea ###

def parse_nft_trades(buys, sells):
    if buys:
        for buy in buys:
            buy['collectionId'] = buy['collection']['id']
            del buy['collection']
        buy_df = pd.DataFrame(buys)
        buy_df['total_amount'] = (buy_df["amount"]).astype("float") * (buy_df["priceETH"]).astype("float")
        buy_df['from'] = buy_df['buyer']
    else:
        buy_df = pd.DataFrame()

    if sells:
        for sell in sells:
            sell['collectionId'] = sell['collection']['id']
            del sell['collection']
        sell_df = pd.DataFrame(sells)
        sell_df['total_amount'] = - (sell_df["amount"]).astype("float") * (sell_df["priceETH"]).astype("float")
        sell_df['from'] = sell_df['seller']
    else:
        sell_df = pd.DataFrame()

    nft_trades = pd.concat((buy_df, sell_df))

    if len(nft_trades) > 1:
        nft_trades['date'] = pd.to_datetime(nft_trades['timestamp'], unit='s')
        nft_trades = nft_trades.sort_values("date")
    return nft_trades

def fetch_nft_trades(account, limit=1000, starting_ts='0', trial=100):
    query = '''{
        trades (first: %i,
            orderBy: timestamp,
            orderDirection: desc,
            where: {
                timestamp_gt: %s,
                %s: %s
            }) {
            id,
            transactionHash,
            timestamp,
            blockNumber,
            isBundle,
            collection { id }
            amount,
            priceETH,
            strategy,
            buyer,
            seller
        }
    }'''
    buys = post_query(
        OPENSEA_URL,
        query %(limit, starting_ts, 'buyer', f'"{account}"'),
        trial=trial
    )['data']['trades']
    sells = post_query(
        OPENSEA_URL,
        query %(limit, starting_ts, 'seller', f'"{account}"'),
        trial=trial
    )['data']['trades']
    return parse_nft_trades(buys, sells)

def opensea_account(df: pd.DataFrame):
    # remove buggy transactions
    df = df.drop_duplicates()
    df = df.dropna(how="any", axis=0)

    df = df[["total_amount", "date"]].rename(columns={"total_amount": "amount"}).set_index("date")
    return df

def opensea_summary(df: pd.DataFrame):
    if len(df) > 0:
        return {
            "n_sells":      len(df[df["total_amount"] < 0]),
            "sell_volume":  abs(df[df["total_amount"] < 0]["total_amount"].sum()).round(2),
            "n_buys":       len(df[df["total_amount"] > 0]),
            "buy_volume":   df[df["total_amount"] > 0]["total_amount"].sum().round(2),
            "avg_time_trades": average_time(df["date"]),
            "nunique_collections": df["collectionId"].nunique()
        }
    else:
        return {
            "n_sells": None,
            "sell_volume": None,
            "n_buys": None,
            "buy_volume": None,
            "avg_time_trades": None,
            "nunique_collections": None
        }
