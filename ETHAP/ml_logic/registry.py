import mlflow
#from colorama import Fore, Style

from ETHAP.ml_logic.params import (
    MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT, MLFLOW_MODEL_NAME, MODEL_TARGET
)

def save_model(model = None) -> None:
    """
    persist trained model, params
    """

    if MODEL_TARGET == "mlflow":

        # retrieve mlflow env params

        # configure mlflow
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(experiment_name=MLFLOW_EXPERIMENT)

        with mlflow.start_run():# STEP 3: push model to mlflowN
            if model is not None:
                mlflow.sklearn.log_model(sk_model=model,
                                       artifact_path="model",
                                       registered_model_name=MLFLOW_MODEL_NAME)

        print("\n✅ data saved to mlflow")

        return None

    print("You can only save the model to MLFlow")

    return None


def load_model():
    """
    load the latest saved model, return None if no model found
    """
    if MODEL_TARGET == "mlflow":
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

    print('You can only load from MLFlow')
