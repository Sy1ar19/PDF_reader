import pdfplumber
import os
from typing import Dict, Any
from PIL import Image
from pyzbar.pyzbar import decode
import io
import fitz


def extract_pdf_data(file_path: str) -> Dict[str, Any]:
    """
    Читает PDF, извлекает текстовую информацию и штрих-коды, возвращает данные в виде словаря.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл '{file_path}' не найден.")

    extracted_data = {"barcodes": [], "raw_text": ""}

    try:
        with pdfplumber.open(file_path) as pdf:
            extracted_data["raw_text"] = "\n".join([page.extract_text() for page in pdf.pages])
    except Exception as e:
        raise RuntimeError(f"Ошибка при обработке текста из PDF: {e}")

    try:
        doc = fitz.open(file_path)

        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            pix = page.get_pixmap()
            img_data = pix.tobytes()
            img = Image.open(io.BytesIO(img_data))
            results = decode(img)

            for result in results:
                barcode_info = {
                    "data": result.data.decode("utf-8"),
                    "type": result.type,
                    "rect": result.rect,
                    "polygon": result.polygon,
                }
                extracted_data["barcodes"].append(barcode_info)
    except Exception as e:
        raise RuntimeError(f"Ошибка при обработке изображений из PDF: {e}")

    return extracted_data


if __name__ == "__main__":
    file_path = "test_task.pdf"
    data = extract_pdf_data(file_path)

    print("\n=== Данные из PDF ===")
    if data["raw_text"]:
        print(data["raw_text"])

    if data["barcodes"]:
        print("\n=== Извлеченные штрих-коды ===")
        for barcode in data["barcodes"]:
            print(f"Штрих-код: {barcode['data']}, Тип: {barcode['type']}, "
                  f"Прямоугольник: {barcode['rect']}, Полигон: {barcode['polygon']}")
    else:
        print("\n❌ Штрих-коды не найдены")
