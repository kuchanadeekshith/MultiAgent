import fitz
import os
import re

def mask_text(text: str) -> str:
    """
    Mask only Name and Email from the text.
    Keep phone, address, and other info intact.
    """
    text= re.sub(r"name\s*\W*(\w*.*)\n", r"Name: [Name_REDACTED]\n", text, flags=re.IGNORECASE)

    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[Email_REDACTED]", text)
    return text

def extract_symptoms(text: str) -> list:
    """
    Simple rule-based symptom extractor.
    """
    symptom_keywords = [
        "cough",
        "fever",
        "shortness of breath",
        "chest pain",
        "fatigue",
        "loss of smell",
        "headache"
    ]
    found = []
    lower_text = text.lower()
    for kw in symptom_keywords:
        if kw in lower_text:
            found.append(kw)
    return found

def ingestion_agent(xray_path: str, pdf_path: str = None) -> dict:
    """
    Validate X-ray path, optionally extract + de-identify PDF,
    return structured info including symptoms.
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

    return {
        "xray_path": xray_path,
        "notes": pdf_text,
        "symptoms": symptoms,
        "patient": {
            "age": 45,
            "allergies": ["ibuprofen"]
        }   
    }
