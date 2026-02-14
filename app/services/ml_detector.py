"""
ML-based scam detection using a pre-trained scikit-learn model.

Module-level singleton:
  - load_model() called once at app startup via lifespan
  - predict_scam_probability(text) called per request
  - Fails silently if model files are missing (returns None)
"""
import os
from typing import Optional

from app.core.logging import logger

# Module-level state — loaded once, reused for every request
_vectorizer = None
_model = None
_model_loaded = False

# Default model directory relative to project root
_DEFAULT_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "ml", "models",
)


def load_model(model_dir: Optional[str] = None) -> bool:
    """
    Load the TF-IDF vectorizer and Logistic Regression model from disk.

    Called once at application startup from app/main.py lifespan.
    Never raises — logs errors and returns False.

    Args:
        model_dir: Directory containing vectorizer.pkl and scam_model.pkl.

    Returns:
        True if loaded successfully, False otherwise.
    """
    global _vectorizer, _model, _model_loaded

    if model_dir is None:
        model_dir = _DEFAULT_MODEL_DIR

    vectorizer_path = os.path.join(model_dir, "vectorizer.pkl")
    model_path = os.path.join(model_dir, "scam_model.pkl")

    if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
        logger.warning(
            f"ML model files not found at {model_dir}. "
            "ML detection disabled. Run 'python -m ml.train_model --data data/scam_dataset.csv' to train."
        )
        _model_loaded = False
        return False

    try:
        import joblib

        _vectorizer = joblib.load(vectorizer_path)
        _model = joblib.load(model_path)
        _model_loaded = True
        logger.info(f"ML scam detection model loaded from {model_dir}")
        return True
    except Exception as exc:
        logger.error(f"Failed to load ML model: {type(exc).__name__}: {exc}")
        _vectorizer = _model = None
        _model_loaded = False
        return False


def is_model_loaded() -> bool:
    """Check if the ML model is loaded and ready for inference."""
    return _model_loaded


def predict_scam_probability(text: str) -> Optional[float]:
    """
    Predict the probability that *text* is a scam message.

    Args:
        text: Message text to classify.

    Returns:
        Float in [0.0, 1.0] where 1.0 = definitely scam.
        Returns None if the model is not loaded.
    """
    if not _model_loaded or _vectorizer is None or _model is None:
        return None

    try:
        features = _vectorizer.transform([text])
        probability = _model.predict_proba(features)[0][1]  # index 1 = P(scam)
        return float(probability)
    except Exception as exc:
        logger.error(f"ML prediction failed: {type(exc).__name__}: {exc}")
        return None
