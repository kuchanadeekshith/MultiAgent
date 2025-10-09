import numpy as np
from PIL import Image
import tensorflow as tf

def imaging_agent(model, xray_path: str) -> dict:
    """
    Runs a lightweight classifier on chest X-ray image.
    Returns probabilities for conditions and severity hint.
    """
    img = Image.open(xray_path).convert("RGB").resize((224, 224))
    img_array = np.expand_dims(np.array(img) / 255.0, axis=0)

    preds = model.predict(img_array)[0]

    condition_probs = {
        "COVID Suspect": float(preds[0]),
        "Pneumonia": float(preds[1]),
        "Normal": float(preds[2])
    }

    # Simple severity logic
    severity = (
        "critical" if preds[0] > 0.7 else
        "moderate" if preds[1] > 0.5 else
        "mild" if preds[2] > 0.5 else
        "unknown"
    )

    return {"condition_probs": condition_probs, "severity_hint": severity}
