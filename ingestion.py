import fitz
import re
import os

def mask_text(text: str) -> str:
    """
    Mask Name and Email in the text. Keep other info intact.
    """
    text = re.sub(r"name\s*\W*(\w*.*)\n", r"Name: [Name_REDACTED]\n", text, flags=re.IGNORECASE)
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[Email_REDACTED]", text)
    return text

def extract_symptoms(text: str) -> list:
    """
    Extract common symptoms using rule-based matching.
    """
    symptom_keywords = ["cough", "fever", "shortness of breath", "chest pain",
                        "fatigue", "loss of smell", "headache"]
    return [kw for kw in symptom_keywords if kw in text.lower()]

def extract_age(text: str) -> int:
    """
    Extract age from text, looking for patterns like 'Age: 45' or 'age 45'.
    Returns None if not found.
    """
    match = re.search(r"age[:\s]*([0-9]{1,3})", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_allergies(text: str) -> list:
    """
    Extract allergies from text using a simple pattern:
    looks for 'allergy: xxx, yyy' or 'allergies: ...'
    """
    match = re.search(r"allerg(?:y|ies)[:\s]*(.*)", text, flags=re.IGNORECASE)
    if match:
        allergies_text = match.group(1)
        # split by comma or semicolon
        allergies = [a.strip() for a in re.split(r"[,;]", allergies_text) if a.strip()]
        return allergies
    return []

def ingestion_agent(xray_path: str, pdf_path: str = None) -> dict:
    """
    Validate X-ray file, optionally extract text from PDF and mask PII.
    Returns structured information including detected symptoms, age, and allergies.
    """
    if not xray_path.lower().endswith((".png", ".jpg", ".jpeg")):
        raise ValueError("Invalid image format. Only PNG, JPG, JPEG allowed.")

    pdf_text = ""
    if pdf_path and os.path.exists(pdf_path):
        with fitz.open(pdf_path) as doc:
            for page in doc:
                pdf_text += page.get_text()
        pdf_text = mask_text(pdf_text)

    symptoms = extract_symptoms(pdf_text)
    age = extract_age(pdf_text)
    allergies = extract_allergies(pdf_text)

    # fallback if not found
    if age is None:
        age = 45  # default
    if not allergies:
        allergies = ["None"]

    return {
        "xray_path": xray_path,
        "notes": pdf_text,
        "symptoms": symptoms,
        "patient": {
            "age": age,
            "allergies": allergies
        }
    }
