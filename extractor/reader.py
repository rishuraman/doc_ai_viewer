# extractor/reader.py

import os
import subprocess
from PyPDF2 import PdfReader

TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # change if different


def read_document(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _read_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return _read_image_with_tesseract(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _read_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text.strip()


def _read_image_with_tesseract(file_path: str) -> str:
    # tesseract <image> stdout --psm 6
    cmd = [TESSERACT_CMD, file_path, "stdout", "--psm", "6"]
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=False
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Tesseract exe not found. Check TESSERACT_CMD in extractor/reader.py."
        )

    if result.returncode != 0:
        print("Tesseract stderr:", result.stderr)
        raise RuntimeError(f"Tesseract failed with code {result.returncode}")

    return result.stdout.strip()
