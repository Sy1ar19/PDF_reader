import pdfplumber
import re
import os
from typing import Dict


def extract_pdf_data(file_path: str) -> Dict[str, str]:
    """
    Читает PDF и извлекает текстовую информацию, возвращая словарь.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл '{file_path}' не найден.")

    extracted_data = {}

    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except Exception as e:
        raise RuntimeError(f"Ошибка при открытии PDF: {e}")

    extracted_data["raw_text"] = text

    fields = {
        "PN": r"PN:\s*([\S]+)",
        "SN": r"SN:\s*([\S]+)",
        "DESCRIPTION": r"DESCRIPTION:\s*([\S]+)",
        "LOCATION": r"LOCATION:\s*([\S]+)",
        "CONDITION": r"CONDITION:\s*([\S]+)",
        "RECEIVER": r"RECEIVER#:\s*([\S]+)",
        "EXP DATE": r"EXP DATE:\s*([\S]+)",
        "PO": r"PO:\s*([\S]+)",
        "CERT SOURCE": r"CERT SOURCE:\s*([\S]+)",
        "REC.DATE": r"REC.DATE:\s*([\S]+)",
        "MFG": r"MFG:\s*([\S]+)",
        "BATCH": r"BATCH#\s*:\s*([\S]+)",
        "DOM": r"DOM:\s*([\S]+)",
        "LOT": r"LOT#\s*:\s*([\S]+)",
        "REMARK": r"REMARK:\s*([\S\s]+?)\s*(?=$|\n[A-Z ]+:)",
        "TAGGED BY": r"TAGGED BY:\s*([\S\s]*?)(?=NOTES:|$)",
        "NOTES": r"NOTES:\s*([\S\s]+?)\s*(?=$|\nQty:|\n[A-Z ]+:)",
        "Qty": r"Qty:\s*(\d+)"
    }

    parsed_data = {}
    seen_keys = set()
    for key, pattern in fields.items():
        matches = re.findall(pattern, text)
        if matches and key not in seen_keys:
            parsed_data[key] = matches[0].strip()
            seen_keys.add(key)

    return parsed_data


if __name__ == "__main__":
    file_path = "test_task_1.pdf"
    data = extract_pdf_data(file_path)

    print("\n=== Данные из PDF ===")
    for k, v in data.items():
        print(f"{k}: {v}")
