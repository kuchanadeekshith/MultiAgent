# therapy.py
import json
import pandas as pd

# Load pharmacies
with open("data\pharmacies.json") as f:
    PHARMACIES = json.load(f)

# Load inventory and meds
INVENTORY = pd.read_csv("data\inventory.csv")
MEDS = pd.read_csv("data\meds.csv")

def therapy_agent(condition_probs: dict, patient_info: dict) -> dict:
    """
    Suggests OTC options based on predicted conditions, checks age/allergy.
    Returns advice text with safety disclaimers.
    """
    # Get main condition (highest probability)
    main_condition = max(condition_probs, key=condition_probs.get)

    # Filter meds for condition
    possible_meds = MEDS[MEDS['indication'].str.contains(main_condition, case=False, na=False)]

    advice_list = []
    for _, med in possible_meds.iterrows():
        # Age check
        if patient_info["age"] < med["age_min"]:
            continue  # Skip medication below age

        # Allergy check
        allergies = [a.lower() for a in patient_info.get("allergies", [])]
        contra_keywords = str(med.get("contra_allergy_keywords", "")).split(";")
        contraindicated = any(word.lower() in allergies for word in contra_keywords)

        advice_list.append({
            "drug_name": med["drug_name"],
            "contraindicated": contraindicated
        })

    # Prepare final advice text
    advice_text = "OTC Medication Suggestions:\n"
    if advice_list:
        for item in advice_list:
            if item["contraindicated"]:
                advice_text += f"- {item['drug_name']} (Contraindicated due to allergy)\n"
            else:
                advice_text += f"- {item['drug_name']}\n"
    else:
        advice_text += "No suitable OTC options found for this patient.\n"

    # Add general disclaimer
    advice_text += "\nNote: This is for informational purposes only. Consult a licensed healthcare professional before taking any medication."

    return {"advice_text": advice_text, "main_condition": main_condition}
