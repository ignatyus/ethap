import pandas as pd
import requests
from google.cloud import bigquery
from google.oauth2 import service_account
import mlflow

UNISWAP_URL = 'https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-ethereum'
OPENSEA_URL = 'https://api.thegraph.com/subgraphs/name/messari/opensea-seaport-ethereum'

PROJECT='on-chain-analytics-ethap'
PUBLIC_PROJECT='bigquery-public-data'
PUBLIC_DATASET='crypto_ethereum'

def average_time(account: pd.Series):
    tmp = account.sort_values()
    return (tmp - tmp.shift(1)).dt.total_seconds().mean()

def post_query(url, query, trial):
    for i in range(trial):
        response = requests.post(url, '', json={'query':query})
        if response.status_code == 200 and 'data' in response.json():
            return response.json()

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
            orderDirection: asc,
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
        swaps_df['date'] = pd.to_datetime(swaps_df['timestamp'], unit='s')
        swaps_df.sort_values("date", inplace=True)

        # Group the transactions by the hash to remove hashes that has more than 1 transaction
        txs = swaps_df.groupby(by="hash").count()[["from"]]
        txs = txs.loc[txs["from"] == 1].index
        swaps_df = swaps_df[swaps_df["hash"].isin(txs)]

        swaps_df = swaps_df.drop_duplicates()
        swaps_df = swaps_df.dropna(how="any", axis=0)
        swaps_df[["amountInUSD", "amountOutUSD"]] = swaps_df[["amountInUSD", "amountOutUSD"]].astype("float")

        # remove transactions that have no value
        swaps_df = swaps_df[(swaps_df['amountInUSD'] != 0) | (swaps_df['amountOutUSD'] != 0)]

        # Fill the transaction amount if one of the values is available
        tmp = swaps_df[swaps_df['amountInUSD'] == 0]['amountOutUSD']
        swaps_df.loc[tmp.index, 'amountInUSD'] = tmp
        tmp = swaps_df[swaps_df['amountOutUSD'] == 0]['amountInUSD']
        swaps_df.loc[tmp.index, 'amountOutUSD'] = tmp


        # Represent the amount as the mean(amountInUSD, amountOutUSD)
        swaps_df["amount"] = (swaps_df["amountInUSD"] + swaps_df["amountOutUSD"]) / 2

    return swaps_df

def uniswap_account(df: pd.DataFrame):
    df = df[["amount", "date"]].set_index("date")
    return df

def uniswap_summary(df: pd.DataFrame):
    if len(df) > 1:
        return {
            "n_swaps":         df["hash"].count(),
            "nunique_pools":   df['poolId'].nunique(),
            "avg_swap_volume": df["amount"].mean().round(2),
            "avg_time_swaps":  average_time(df["date"]).round(2)
        }
    else:
        return {
            "n_swaps":         None,
            "nunique_pools":   None,
            "avg_swap_volume": None,
            "avg_time_swaps":  None
        }




# NFT/OPENSEA

def parse_buys(df: pd.DataFrame):
    df['total_amount'] = (df["amount"]).astype("float") * (df["priceETH"]).astype("float")
    df['from'] = df['buyer']
    return df

def parse_sells(df: pd.DataFrame):
    df['total_amount'] = - (df["amount"]).astype("float") * (df["priceETH"]).astype("float")
    df['from'] = df['seller']
    return df

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
        sell_df['total_amount'] = (sell_df["amount"]).astype("float") * (sell_df["priceETH"]).astype("float")
        sell_df['from'] = sell_df['buyer']
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
            orderDirection: asc,
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
    if len(df) > 1:
        return {
            "n_sells":      len(df[df["total_amount"] < 0]),
            "sell_volume":  abs(df[df["total_amount"] < 0]["total_amount"].sum()).round(2),
            "n_buys":       len(df[df["total_amount"] > 0]),
            "buy_volume":   df[df["total_amount"] > 0]["total_amount"].sum().round(2),
            "avg_time_trades": average_time(df["date"]).round(2),
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


# PUBLIC QUERY

def fetch_parse_public_tansaction(table, account, secrets, limit=1000):
    query = f'''
        SELECT *
        FROM `{PUBLIC_PROJECT}.{PUBLIC_DATASET}.{table}`
        WHERE from_address = "{account}" OR to_address = "{account}"
        LIMIT {limit}
    '''
    credentials = service_account.Credentials.from_service_account_info(
        secrets
    )
    client = bigquery.Client(credentials=credentials)
    query_job = client.query(query)
    df = query_job.to_dataframe()

    from_df = df[df["from_address"] == account]
    if len(from_df) > 0:
        from_df["direction"] = 'sender'
        from_df["account"] = account
    else:
        from_df["direction"] = None
        from_df["account"] = None

    from_df.drop(columns=["from_address", "to_address"])

    to_df = df[df["to_address"] == account]
    if len(to_df) > 0:
        to_df["direction"] = 'receiver'
        to_df["account"] = account
    else:
        to_df["direction"] = None
        to_df["account"] = None

    to_df.drop(columns=["from_address", "to_address"])

    df = pd.concat((from_df, to_df))
    df = df.drop_duplicates()
    df = df.dropna(how="any", axis=0)

    return df.sort_values("block_timestamp")

def transfers_summary(df: pd.DataFrame):
    if len(df) > 0:
        return {
            "n_sent": len(df[df["direction"] == "sender"]),
            "n_received": len(df[df["direction"] == "receiver"]),
            "nunique_tokens": df["token_address"].nunique(),
            "avg_time_transfers": average_time(df["block_timestamp"]).round(2)
        }
    else:
        return {
            "n_sent": None,
            "n_received": None,
            "nunique_tokens": None,
            "avg_time_transfers": None
        }


 # MLFlow
def load_model(params):
    MLFLOW_TRACKING_URI = params['MLFLOW_TRACKING_URI']
    MLFLOW_MODEL_NAME = params['MLFLOW_MODEL_NAME']
    """
    load the latest saved model, return None if no model found
    """
    stage = "Production"

    print(f"\nLoad model {stage} stage from mlflow...")

    # load model from mlflow
    model = None

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    model_uri = f"models:/{MLFLOW_MODEL_NAME}/{stage}"
    print(f"- uri: {model_uri}")

    try:
        model = mlflow.sklearn.load_model(model_uri=model_uri)
        print("\n✅ model loaded from mlflow")
    except:
        print(f"\n❌ no model in stage {stage} on mlflow")
        return None
    return model
