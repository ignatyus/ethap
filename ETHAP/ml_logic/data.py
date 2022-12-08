import os
import pandas as pd
from ETHAP.data_sources.local_disk import save_local, get_local_chunk
from ETHAP.data_sources.big_query import save_bq, get_bq_chunk
from ETHAP.ml_logic.params import CHUNK_SIZE

from colorama import Fore, Style

def get_data(source_name: str,
             public: bool,
             index: int = 0,
             verbose=False,
             save_dataset: bool=False,
             is_first: bool = True) -> pd.DataFrame:
    """
    Return a `chunk_size` rows from the source dataset, starting at row `index` (included)
    Always assumes `source_name` (CSV or Big Query table) have headers,
    and do not consider them as part of the data `index` count.

    Params
    --------
    source_name: table name (cloud), or filename (local) without extenstion, e.g. '.csv'
    index: the starting row to be fetched.
    save_dataset: whether to save dataset locally or to bigquery.
    is_first: when True, saved data will be in write mode.
    """
    assert "." not in source_name, "'source_name' can not contain extension."
    chunk_size = int(CHUNK_SIZE)
    if os.environ.get("DATA_SOURCE") == "cloud":

        print(Fore.BLUE + f"\nFetching dataset from bigquery with {CHUNK_SIZE} samples..." + Style.RESET_ALL)

        data = get_bq_chunk(table=source_name,
                            public=public,
                            index=index,
                            chunk_size=chunk_size,
                            verbose=verbose)

    else:
        data = get_local_chunk(table=source_name,
                               index=index,
                               chunk_size=chunk_size,
                               verbose=verbose)

    if save_dataset:
        save_data(data=data,
                  table_name=source_name,
                  is_first=is_first)

    return data

def save_data(data: pd.DataFrame,
              table_name: str,
              is_first: bool = True) -> None:
    """
    save dataset to big query or local
    ----------
    table: name of target table
    data: dataframe data
    is_first: empty the table beforehands if `is_first` is True
    """
    assert "." not in table_name, "'table_name' can not contain extension."

    if os.environ.get("MODEL_TARGET") == "cloud":

        save_bq(table=table_name,
                data=data,
                is_first=is_first)
        return

    save_local(table=table_name,
               data=data,
               is_first=is_first)
