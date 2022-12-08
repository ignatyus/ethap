import requests
import pandas as pd
from ETHAP.data_sources.big_query import save_bq
from google.cloud import bigquery
from ETHAP.ml_logic.params import PROJECT, DATASET

UNISWAP_URL = 'https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-ethereum'
OPENSEA_URL = 'https://api.thegraph.com/subgraphs/name/messari/opensea-seaport-ethereum'

UNISWAP_QUERY = '''{
    swaps  (first: %i,
            orderBy: timestamp,
            orderDirection: asc,
            where: { timestamp_gt: %s }) {
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
OPENSEA_QUERY = '''{
    trades (first: %i,
            orderBy: timestamp,
            orderDirection: asc,
            where: { timestamp_gt: %s }) {
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

def fetch_uniswap(source='uniswap_swaps', limit=1_000, starting_ts='0',
                  trial=1000, last_ts=1670189939, is_first=True):
    print('Start of fetch_uniswap')
    if not is_first:
        client = bigquery.Client()
        sql = f'''
            SELECT `timestamp`
            FROM `{PROJECT}.{DATASET}.{source}`
            ORDER BY `timestamp` DESC
            LIMIT 1
        '''
        answer = client.query(sql, project=PROJECT)
        starting_ts = [r[0] for r in answer.result()][0]

    swaps = []
    count = 0

    while int(starting_ts) < last_ts:
        result = post_query(
            url=UNISWAP_URL,
            query=UNISWAP_QUERY %(limit, starting_ts),
            trial=trial
        )['data']['swaps']
        swaps += parse_swaps(result)
        starting_ts = result[-1]['timestamp']

        if count == 100 or int(starting_ts) >= last_ts:
            save_bq(source, pd.DataFrame(swaps), is_first=is_first)
            if is_first: is_first = False
            swaps = []
            count = 0

        count += 1
    print('End of fetch_uniswap')


def parse_nft_trades(nft_trades):
    for trade in nft_trades:
        trade['collectionId'] = trade['collection']['id']
        del trade['collection']
    return nft_trades

def fetch_opensea(source ='opensea_trades', limit=1_000, starting_ts='0',
                  trial=100, last_ts=1670189939, is_first=True):
    print('Start of fetch_opensea')
    if not is_first:
        client = bigquery.Client()
        sql = f'''
            SELECT `timestamp`
            FROM `{PROJECT}.{DATASET}.{source}`
            ORDER BY `timestamp` DESC
            LIMIT 1
        '''
        answer = client.query(sql, project=PROJECT)
        starting_ts = [r[0] for r in answer.result()][0]

    trades = []
    count = 0

    while int(starting_ts) < last_ts:
        result = post_query(
            url=OPENSEA_URL,
            query=OPENSEA_QUERY %(limit, starting_ts),
            trial=trial
        )['data']['trades']
        trades += parse_nft_trades(result)
        starting_ts = result[-1]['timestamp']

        if count == 1_000 or int(starting_ts) >= last_ts:
            save_bq(source, pd.DataFrame(trades), is_first=is_first)
            if is_first: is_first = False
            trades = []
            count = 0

        count += 1
    print('End of fetch_opensea')
