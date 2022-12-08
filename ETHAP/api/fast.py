from fastapi import FastAPI
from ETHAP.ml_logic.registry import load_model
from ETHAP.ml_logic.preprocessor import  feature_engineer
import pandas as pd

app = FastAPI()


app.state.model = load_model()
# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': True}

@app.get("/predict")
def predict(n_sells: int,
            sell_volume: float,
            n_buys: int,
            buy_volume: float,
            nunique_collections: int,
            avg_time_trades: float,
            n_swaps:int,
            nunique_pools:int,
            avg_swap_volume:float,
            avg_time_swaps:float,
            n_sent:int,
            n_received:int,
            nunique_tokens:int,
            avg_time_transfers:float):      # 1
    """
    we use type hinting to indicate the data types expected
    for the parameters of the function
    FastAPI uses this information in order to hand errors
    to the developpers providing incompatible parameters
    FastAPI also provides variables of the expected data type to use
    without type hinting we need to manually convert
    the parameters of the functions which are all received as strings
    """

    #account = "2013-07-06 17:18:00.000000119"

    X_pred = pd.DataFrame(dict(
        n_sells=[n_sells],
        sell_volume=[sell_volume],
        n_buys=[n_buys],
        buy_volume=[buy_volume],
        nunique_collections=[nunique_collections],
        avg_time_trades=[avg_time_trades],
        n_swaps=[n_swaps],
        nunique_pools=[nunique_pools],
        avg_swap_volume=[avg_swap_volume],
        avg_time_swaps=[avg_time_swaps],
        n_sent=[n_sent],
        n_received=[n_received],
        nunique_tokens=[nunique_tokens],
        avg_time_transfers=[avg_time_transfers]))

    model = app.state.model
    y_pred = model.predict(X_pred)[0]


    return dict(pred=float(y_pred))
