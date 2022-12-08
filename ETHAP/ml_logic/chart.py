import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_2d(df:pd.DataFrame, sample:int=1000, x:str=None, y:str=None, hue:str=None, highlight:list=None, log_scale: bool=True, size_base:str = None):
    if sample:
        df = df.sample(sample)

    fig = px.scatter(df, x=x, y=y, color=hue, log_y=log_scale, log_x=log_scale, size=size_base)

    # if highlight:
    #     fig.add_trace(go.Scatter(x=highlight[0], y=highlight[1], mode = 'markers',
    #                   marker_symbol = 'star',
    #                   marker_size = 15))
    return fig.show()



def plot_3d(df:pd.DataFrame, sample:int=1000, x:str=None, y:str=None, z:str=None, hue:str=None, log_scale: bool=True, opacity:float=0.6, size_base:str = None):
    if sample:
        df = df.sample(sample)
    fig = px.scatter_3d(df, x=x, y=y, z=z, color=hue, opacity=opacity, log_x=log_scale, log_y=log_scale, size=size_base)

    return fig.show()
