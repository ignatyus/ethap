import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from ETHAP.utils.data import average_time

PROJECT='wagon-bootcamp-364813'
PUBLIC_PROJECT='bigquery-public-data'
PUBLIC_DATASET='crypto_ethereum'

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
