import mlflow

def load_model(params):
    MLFLOW_TRACKING_URI = params['MLFLOW_TRACKING_URI']
    MLFLOW_MODEL_NAME = params['MLFLOW_MODEL_NAME']
    """
    load the latest saved model, return None if no model found
    """
    stage = "Production"

    print(f"\nLoad model {stage} stage from mlflow...")

    # load model from mlflow
    model = None

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    model_uri = f"models:/{MLFLOW_MODEL_NAME}/{stage}"
    print(f"- uri: {model_uri}")

    try:
        model = mlflow.sklearn.load_model(model_uri=model_uri)
        print("\n✅ model loaded from mlflow")
    except:
        print(f"\n❌ no model in stage {stage} on mlflow")
        return None
    return model
