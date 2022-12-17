import pandas as pd

def average_time(account: pd.Series):
    if len(account) > 1:
        tmp = account.sort_values()
        return int((tmp - tmp.shift(1)).dt.total_seconds().mean())

def combine_account_info(opensea_dict, uniswap_dict, transfers_dict):
    return pd.DataFrame(dict(
        n_sells=[opensea_dict['n_sells']],
        sell_volume=[opensea_dict['sell_volume']],
        n_buys=[opensea_dict['n_buys']],
        buy_volume=[opensea_dict['buy_volume']],
        nunique_collections=[opensea_dict['nunique_collections']],
        avg_time_trades=[opensea_dict['avg_time_trades']],
        n_swaps=[uniswap_dict['n_swaps']],
        nunique_pools=[uniswap_dict['nunique_pools']],
        avg_swap_volume=[uniswap_dict['avg_swap_volume']],
        avg_time_swaps=[uniswap_dict['avg_time_swaps']],
        n_sent=[transfers_dict['n_sent']],
        n_received=[transfers_dict['n_received']],
        nunique_tokens=[transfers_dict['nunique_tokens']],
        avg_time_transfers=[transfers_dict['avg_time_transfers']]
    ))
