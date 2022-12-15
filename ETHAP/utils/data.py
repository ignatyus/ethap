import pandas as pd

def average_time(account: pd.Series):
    tmp = account.sort_values()
    return (tmp - tmp.shift(1)).dt.total_seconds().mean()
