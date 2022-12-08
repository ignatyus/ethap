import numpy as np
import pandas as pd

from colorama import Fore, Style

from ETHAP.ml_logic.data import get_data, save_data
from ETHAP.ml_logic.model import K_means_model
from ETHAP.ml_logic.params import CHUNK_SIZE, DATASET_SIZE
from ETHAP.ml_logic.preprocessor import feature_engineer
from ETHAP.utils import islile
from ETHAP.ml_logic.registry import get_model_version

from ETHAP.ml_logic.registry import load_model, save_model


def preprocess(source_name,public):
    """
    Preprocess the dataset by chunks fitting in memory.

    """

    print("\n⭐️ Use case: preprocess")

    # Iterate on the dataset, in chunks
    chunk_id = 0
    row_count = 0
    cleaned_row_count = 0

    while (True):
        print(Fore.BLUE + f"\nProcessing chunk n°{chunk_id}..." + Style.RESET_ALL)

        data_chunk = get_data(
            source_name=source_name,
            public=public
            index=chunk_id * CHUNK_SIZE,
            verbose=False,
            save_dataset=False,
            is_first=True)

        # Break out of while loop if data is none
        if data_chunk is None:
            print(Fore.BLUE + "\nNo data in latest chunk..." + Style.RESET_ALL)
            break

        row_count += data_chunk.shape[0]

        #data_chunk_cleaned = clean_data(data_chunk)

        cleaned_row_count += len(data_chunk)

        # Break out of while loop if cleaning removed all rows
        if len(data_chunk) == 0:
            print(Fore.BLUE + "\nNo cleaned data in latest chunk..." + Style.RESET_ALL)
            break

        X_chunk = data_chunk


        X_processed_chunk = feature_engineer(X_chunk)

        #data_processed_chunk = pd.DataFrame(
        #    np.concatenate((X_processed_chunk, y_chunk), axis=1)
        #)

        # Save and append the chunk
        is_first = chunk_id == 0

        table_name="data of ETHAP"

        save_data(data= X_processed_chunk,table_name=table_name,is_first=True)



        chunk_id += 1

    if row_count == 0:
        print("\n✅ No new data for the preprocessing 👌")
        return None

    print(f"\n✅ Data processed saved entirely: {row_count} rows ({cleaned_row_count} cleaned)")

    return None

def train():
    """
    Train a new model on the full (already preprocessed) dataset ITERATIVELY, by loading it
    chunk-by-chunk, and updating the weight of the model after each chunks.
    Save final model once it has seen all data, and compute validation metrics on a holdout validation set
    common to all chunks.
    """
    print("\n⭐️ Use case: train")

    print(Fore.BLUE + "\nLoading preprocessed validation data..." + Style.RESET_ALL)



    model = None
    model = load_model()  # production model


    # Iterate on the full dataset per chunks
    chunk_id = 0
    row_count = 0
    metrics_val_list = []

    while (True):

        print(Fore.BLUE + f"\nLoading and training on preprocessed chunk n°{chunk_id}..." + Style.RESET_ALL)

        data_processed_chunk = get_data(
            source_name=f"train_processed_{DATASET_SIZE}",
            public=False,
            index=chunk_id * CHUNK_SIZE,
            verbose=False,
            save_dataset=False,
            is_first=True
        )


        # Check whether data source contain more data
        if data_processed_chunk is None:
            print(Fore.BLUE + "\nNo more chunk data..." + Style.RESET_ALL)
            break

        data_processed_chunk = data_processed_chunk.to_numpy()

        X_train_chunk = data_processed_chunk


        # Increment trained row count
        chunk_row_count = data_processed_chunk.shape[0]
        row_count += chunk_row_count

        # Initialize model
        if model is None:
            model = K_means_model(X_train_chunk)

        # (Re-)compile and train the model incrementally




        # Check if chunk was full
        if chunk_row_count < CHUNK_SIZE:
            print(Fore.BLUE + "\nNo more chunks..." + Style.RESET_ALL)
            break

        chunk_id += 1

    if row_count == 0:
        print("\n✅ no new data for the training 👌")
        return




    # Save model
    save_model(model=model)

    return model



def pred(X_pred: pd.DataFrame = None) -> np.ndarray:
    """
    Make a prediction using the latest trained model
    """

    print("\n⭐️ Use case: predict")

    from ETHAP.ml_logic.registry import load_model

    model = load_model()

    X_processed = preprocess_features(X_pred)

    y_pred = model.predict(X_processed)

    print("\n✅ prediction done: ", y_pred, y_pred.shape)

    return y_pred


if __name__ == '__main__':
    preprocess()
  #  preprocess(source_type='val')
    train()
    pred()
