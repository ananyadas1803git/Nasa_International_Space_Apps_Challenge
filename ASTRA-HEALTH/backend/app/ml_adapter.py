"""ML integration boundary (blueprint 11.3 / 11.4).

frontend -> website backend -> THIS ADAPTER -> model -> backend -> frontend.
The ML team has not delivered a model, dataset or schema yet, so by default nothing is predicted.
When the real model exists, only `run_model()` below needs to change - routes and UI stay the same.
Mock output is clearly labelled and is never stored as a real prediction.
"""
from .config import ML_MODE

FEATURES = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature_c", "glucose_mg_dl", "sleep_hours", "stress_score", "radiation_msv"]


def run_model(features: dict) -> dict:
    """TODO(ML team): load/call the real model here and map its output to the dict returned by predict()."""
    raise NotImplementedError


def predict(features: dict) -> dict:
    base = {"mode": ML_MODE, "input_schema": FEATURES}
    if ML_MODE == "off":
        return {**base, "available": False, "is_real_model": False, "source": "none",
                "message": "No ML model is connected yet. Awaiting dataset, schema and model from the ML team."}
    if ML_MODE == "mock":
        return {**base, "available": True, "is_real_model": False, "source": "MOCK", "model_version": "mock-0",
                "task": "placeholder", "label": "MOCK OUTPUT - NOT A PREDICTION", "score": None, "confidence": None,
                "message": "Placeholder used to test the UI/API integration. Not produced by a trained model."}
    try:
        out = run_model(features)
        return {**base, "available": True, "is_real_model": True, "source": "model", **out}
    except NotImplementedError:
        return {**base, "available": False, "is_real_model": False, "source": "none",
                "message": "ML_MODE is set but run_model() is not implemented yet."}
    except Exception as exc:  # model failure must never break the website (fallback behaviour)
        return {**base, "available": False, "is_real_model": False, "source": "error",
                "message": f"Model call failed: {exc}"}
