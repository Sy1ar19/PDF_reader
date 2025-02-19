from extract_pdf_data import extract_pdf_data
from typing import Dict, Any


def validate_pdf_structure(test_file_path: str, reference_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Проверяет, соответствует ли структура тестового PDF эталону, включая текст и штрих-коды.
    """
    try:
        test_data = extract_pdf_data(test_file_path)
    except RuntimeError as e:
        return {"valid": False, "error": str(e)}

    ref_text = reference_data.get("raw_text", "")
    test_text = test_data.get("raw_text", "")

    ref_lines = ref_text.split("\n")
    test_lines = test_text.split("\n")

    missing_lines = [line for line in ref_lines if line not in test_lines]
    extra_lines = [line for line in test_lines if line not in ref_lines]

    ref_barcodes = reference_data.get("barcodes", [])
    test_barcodes = test_data.get("barcodes", [])

    missing_barcodes = []
    extra_barcodes = []
    barcode_location_errors = []

    for ref_barcode in ref_barcodes:
        found = False
        for test_barcode in test_barcodes:
            if ref_barcode["data"] == test_barcode["data"]:
                found = True

                if ref_barcode["type"] != test_barcode["type"]:
                    barcode_location_errors.append({
                        "barcode": ref_barcode["data"],
                        "expected_type": ref_barcode["type"],
                        "found_type": test_barcode["type"]
                    })

                if ref_barcode["rect"] != test_barcode["rect"]:
                    barcode_location_errors.append({
                        "barcode": ref_barcode["data"],
                        "expected_rect": ref_barcode["rect"],
                        "found_rect": test_barcode["rect"]
                    })

                if ref_barcode["polygon"] != test_barcode["polygon"]:
                    barcode_location_errors.append({
                        "barcode": ref_barcode["data"],
                        "expected_polygon": ref_barcode["polygon"],
                        "found_polygon": test_barcode["polygon"]
                    })
        if not found:
            missing_barcodes.append(ref_barcode["data"])

    for test_barcode in test_barcodes:
        found = False
        for ref_barcode in ref_barcodes:
            if test_barcode["data"] == ref_barcode["data"]:
                found = True
        if not found:
            extra_barcodes.append(test_barcode["data"])

    return {
        "valid": not missing_lines and not extra_lines and not missing_barcodes and not extra_barcodes and not barcode_location_errors,
        "missing_lines": missing_lines,
        "extra_lines": extra_lines,
        "missing_barcodes": missing_barcodes,
        "extra_barcodes": extra_barcodes,
        "barcode_location_errors": barcode_location_errors,
        "test_data": test_data
    }


if __name__ == "__main__":
    reference_file = "test_task.pdf"
    test_file = "test_task_9.pdf"

    reference_data = extract_pdf_data(reference_file)
    result = validate_pdf_structure(test_file, reference_data)

    print("\n=== Проверка структуры PDF ===")
    if result["valid"]:
        print("✅ Тестовый PDF соответствует эталону!")
    else:
        print("❌ Структура PDF не соответствует эталону.")
        if "error" in result:
            print(f"Ошибка: {result['error']}")
        if result["missing_lines"]:
            print(f"Отсутствуют строки:\n{result['missing_lines']}")
        if result["extra_lines"]:
            print(f"Лишние строки:\n{result['extra_lines']}")
        if result["missing_barcodes"]:
            print(f"Отсутствуют штрих-коды:\n{result['missing_barcodes']}")
        if result["extra_barcodes"]:
            print(f"Лишние штрих-коды:\n{result['extra_barcodes']}")
        if result["barcode_location_errors"]:
            print(f"Ошибки расположения штрих-кодов:\n{result['barcode_location_errors']}")
