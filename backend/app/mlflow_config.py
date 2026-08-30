import os
import mlflow
from mlflow.tracking import MlflowClient

def configure_mlflow():
    """Configure MLflow tracking"""
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("sqlite:///mlflow.db")

    # Create experiment if it doesn't exist
    experiment_name = "Supply_Chain_Forecasting"
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
        else:
            experiment_id = experiment.experiment_id
    except Exception:
        # Fallback to default experiment
        experiment_id = "0"

    mlflow.set_experiment(experiment_name)
    return experiment_name

def log_model_metrics(run_name: str, metrics: dict, params: dict = None, artifacts: dict = None):
    """Log model metrics, parameters, and artifacts to MLflow"""
    with mlflow.start_run(run_name=run_name):
        # Log parameters
        if params:
            for key, value in params.items():
                mlflow.log_param(key, value)

        # Log metrics
        if metrics:
            for key, value in metrics.items():
                mlflow.log_metric(key, value)

        # Log artifacts
        if artifacts:
            for key, value in artifacts.items():
                if isinstance(value, str) and os.path.exists(value):
                    mlflow.log_artifact(value, key)
                else:
                    # Log as text artifact
                    temp_file = f"/tmp/{key}.txt"
                    with open(temp_file, 'w') as f:
                        f.write(str(value))
                    mlflow.log_artifact(temp_file, key)

def get_model_versions(model_name: str):
    """Get all versions of a registered model"""
    client = MlflowClient()
    try:
        versions = client.get_latest_versions(model_name)
        return versions
    except Exception:
        return []

def register_model(run_id: str, model_name: str):
    """Register a model in MLflow Model Registry"""
    try:
        result = mlflow.register_model(
            f"runs:/{run_id}/model",
            model_name
        )
        return result
    except Exception as e:
        print(f"Model registration failed: {e}")
        return None

def load_model(model_name: str, version: str = "latest"):
    """Load a registered model"""
    try:
        if version == "latest":
            model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
        else:
            model = mlflow.pyfunc.load_model(f"models:/{model_name}/{version}")
        return model
    except Exception as e:
        print(f"Model loading failed: {e}")
        return None