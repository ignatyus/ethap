from google.cloud import bigquery
from colorama import Fore, Style
import pandas as pd

from ETHAP.ml_logic.params import PUBLIC_PROJECT, PUBLIC_DATASET, CHUNK_SIZE, PROJECT, DATASET

def get_bq_chunk(table: str,
                 public: bool,
                 index: int = 0,
                 chunk_size: int = CHUNK_SIZE,
                 verbose=True) -> pd.DataFrame:
    """
    return a 'chunk_size' of big query dataset table
    format the output dataframe according to the provided data types
    """
    if verbose:
        print(Fore.MAGENTA + f"Source data from big query {table}: {chunk_size if chunk_size is not None else 'all'} rows (from row {index})" + Style.RESET_ALL)

    if public:
        table = f"{PUBLIC_PROJECT}.{PUBLIC_DATASET}.{table}"
    else:
        table = f"{PROJECT}.{DATASET}.{table}"

    client = bigquery.Client()

    rows = client.list_rows(table,
                            start_index=index,
                            max_results=int(chunk_size))

    # convert to expected data types
    big_query_df = rows.to_dataframe()

    if big_query_df.shape[0] == 0:
        print("Dataframe don't have any content. Query failed.")
        return None  # end of data

    return big_query_df

def save_bq(table: str,
               data: pd.DataFrame,
               is_first: bool):
    """
    save dataset to big query
    """

    print(Fore.BLUE + f"\nSaving data to big query {table}:" + Style.RESET_ALL)

    # $CHA_BEGIN
    table = f"{PROJECT}.{DATASET}.{table}"

    # bq requires str columns starting with a letter or underscore
    data.columns = [f"_{column}" if type(column) != str else column for column in data.columns]

    client = bigquery.Client()

    # define write mode and schema
    write_mode = "WRITE_TRUNCATE" if is_first else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    print(f"\n{'Write' if is_first else 'Append'} {table} ({data.shape[0]} rows)")

    # load data
    job = client.load_table_from_dataframe(data, table, job_config=job_config)
    result = job.result()  # wait for the job to complete

    print(Fore.BLUE + f"\nData saved" + Style.RESET_ALL)
