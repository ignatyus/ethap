import pandas as pd
import os

from colorama import Fore, Style
from ETHAP.ml_logic.params import LOCAL_DATA_PATH, LOCAL_REGISTRY_PATH


def get_local_chunk(table: str,
                     index: int,
                     chunk_size: int,
                     verbose: bool=True) -> pd.DataFrame:
    """
    return a chunk of the raw dataset from local disk or cloud storage
    """
    path = os.path.join(
        os.path.expanduser(LOCAL_DATA_PATH),
        f"{table}.csv")

    chunk_size = int(chunk_size)
    if verbose:
        print(Fore.MAGENTA + f"Source data from {path}: {chunk_size if chunk_size is not None else 'all'} rows (from row {index})" + Style.RESET_ALL)

    try:

        df = pd.read_csv(
                path,
                skiprows=index + 1,  # skip header
                nrows=chunk_size,
                header=None)  # read all rows

        # read_csv(dtypes=...) will silently fail to convert data types, if column names do no match dictionnary key provided.
        # if isinstance(dtypes, dict):
        #     assert dict(df.dtypes) == dtypes

        # if columns is not None:
        #     df.columns = columns

    except pd.errors.EmptyDataError:

        return None  # end of data

    return df

def save_local(table: str,
               data: pd.DataFrame,
               is_first: bool):
    """
    save dataset to local disk
    """

    path = os.path.join(os.path.expanduser(LOCAL_REGISTRY_PATH), f"{table}.csv")
    print(Fore.BLUE + f"\nSaving data to {path}:" + Style.RESET_ALL)

    data.to_csv(path,
                mode="w" if is_first else "a",
                header=is_first,
                index=False)
    print(Fore.BLUE + f"\nData saved" + Style.RESET_ALL)
