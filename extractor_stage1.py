import pdfplumber
import pytesseract
from PIL import Image
import json
import os
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text.strip()

def extract_from_email(text):
    return text.strip()

def detect_file_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return "pdf"
    elif ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]:
        return "image"
    elif ext == ".txt":
        return "txt"
    else:
        return "unknown"

def process_document(file_path):
    file_type = detect_file_type(file_path)
    file_name = os.path.basename(file_path)

    print(f"\n Processing: {file_name}")
    print(f" Type detected: {file_type}")

    if file_type == "pdf":
        raw_text = extract_from_pdf(file_path)
    elif file_type == "image":
        raw_text = extract_from_image(file_path)
    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    else:
        print(" Unsupported file type.")
        return None

    result = {
        "file_name": file_name,
        "file_type": file_type,
        "processed_at": datetime.now().isoformat(),
        "character_count": len(raw_text),
        "raw_text": raw_text
    }

    output_file = os.path.join(
        "outputs",
        file_name.replace(".", "_") + "_extracted.json"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f" Characters extracted: {len(raw_text)}")
    print(f" Saved to: {output_file}")
    print(f"\n --- Preview (first 300 chars) ---")
    print(raw_text[:300])
    print(f" ---------------------------------")

    return result

def process_email_text(email_text, label="email_input"):
    raw_text = extract_from_email(email_text)

    result = {
        "file_name": label,
        "file_type": "email",
        "processed_at": datetime.now().isoformat(),
        "character_count": len(raw_text),
        "raw_text": raw_text
    }

    output_file = os.path.join("outputs", label + "_extracted.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n Email text processed.")
    print(f" Characters: {len(raw_text)}")
    print(f" Saved to: {output_file}")
    print(f"\n --- Preview (first 300 chars) ---")
    print(raw_text[:300])
    print(f" ---------------------------------")

    return result


if __name__ == "__main__":

    print("=== Stage 1: Document Ingestion & Text Extraction ===\n")

    for filename in os.listdir("inputs"):
        file_path = os.path.join("inputs", filename)
        if os.path.isfile(file_path):
            process_document(file_path)

    sample_email = """
    Dear all, kindly note that the IA-2 exam for 3rd year CSE students
    originally scheduled on 18th May 2026 has been postponed to 22nd May 2026.
    Venue remains Block C, Room 204.
    This is due to unavailability of faculty.
    Students are advised to take note and prepare accordingly.
    - Dr. Ramesh Kumar, HOD CSE
    """
    process_email_text(sample_email, label="exam_reschedule_email")