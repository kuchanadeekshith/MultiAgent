
import os

def imaging_agent(xray_path: str) -> dict:
    """
    Actually we have to run a ml model on the picture but we are not as it a demo 
    we are condidering the output on assumption considering its filename
    """

    # Get just the file name
    filename = os.path.basename(xray_path).lower()

    # Rule-based mock logic
    if "covid" in filename:
        condition_probs = {
            "covid_suspect": 0.65,
            "pneumonia": 0.25,
            "normal": 0.10
        }
        severity_hint = "moderate"

    elif "pneumonia" in filename:
        condition_probs = {
            "pneumonia": 0.70,
            "covid_suspect": 0.15,
            "normal": 0.15
        }
        severity_hint = "moderate"

    elif "normal" in filename:
        condition_probs = {
            "normal": 0.80,
            "pneumonia": 0.10,
            "covid_suspect": 0.10
        }
        severity_hint = "none"

    else:

        condition_probs = {
            "normal": 0.5,
            "pneumonia": 0.444,
            "covid_suspect": 0.333
        }
        severity_hint = "mild"

    return {
        "condition_probs": condition_probs,
        "severity_hint": severity_hint
    }
