"""
model package params
load and validate the environment variables in the `.env`
"""

import os

LOCAL_DATA_PATH = os.path.expanduser(os.environ.get("LOCAL_DATA_PATH"))
LOCAL_REGISTRY_PATH = os.path.expanduser(os.environ.get("LOCAL_REGISTRY_PATH"))
DATASET_SIZE = os.environ.get("DATASET_SIZE")
CHUNK_SIZE = os.environ.get("CHUNK_SIZE")

# MLFlow
MODEL_TARGET = os.environ.get("MODEL_TARGET")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")
MLFLOW_EXPERIMENT = os.environ.get("MLFLOW_EXPERIMENT")
MLFLOW_MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME")

# GCP
PROJECT = os.environ.get("PROJECT")
DATASET = os.environ.get("DATASET")

PUBLIC_PROJECT = os.environ.get("PUBLIC_PROJECT")
PUBLIC_DATASET = os.environ.get("PUBLIC_DATASET")
