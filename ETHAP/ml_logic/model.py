
from colorama import Fore, Style

import time
print(Fore.BLUE + "\nLoading tensorflow..." + Style.RESET_ALL)
start = time.perf_counter()

#from tensorflow.keras import Model, Sequential, layers, regularizers, optimizers
#from tensorflow.keras.callbacks import EarlyStopping

end = time.perf_counter()
print(f"\n✅ tensorflow loaded ({round(end - start, 2)} secs)")

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

def K_means_model(X: pd.DataFrame):
    """
    Initialize the K-means model
    """
    print(Fore.BLUE + "\nInitialize model..." + Style.RESET_ALL)

    model=KMeans(n_clusters=10, random_state=0).fit(X)

    print("\n✅ model initialized")
    return model

########################################

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np

def pca_kmeans(X:pd.DataFrame, n_clusters:int=8, impute_df:bool=False)  -> pd.DataFrame:
    '''
    X: dataframe input
    n_clusters: number of labels for KMeans clustering
    impute_df: whether to return the imputed version of X dataframe, if False, return dataframe in original version with a new label column
    '''
    X_copy = X.copy()
    # Data preprocess

    X = X.select_dtypes(include=np.number)
    if "Unnamed: 0" in X.columns:
        X = X.drop("Unnamed: 0", axis=1)
        col = X.columns
    else:
        col = X.columns
    imputer =  SimpleImputer(missing_values=np.nan, strategy="median")
    X = pd.DataFrame(imputer.fit_transform(X))
    X.columns = col

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA
    pca = PCA().fit(X_scaled)
    X_proj = pca.transform(X_scaled)
    X_proj = pd.DataFrame(X_proj, columns=[f'PC{i}' for i in range(1, X_scaled.shape[1]+1)])

    # KMeans
    km = KMeans(n_clusters=n_clusters)
    km.fit(X_proj)

    X_copy["label"] = km.labels_

    if impute_df:
        X["label"] = km.labels_

        return X

    return X_copy
