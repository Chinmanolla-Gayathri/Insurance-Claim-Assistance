import os
import sys
import easyocr
from pdf2image import convert_from_path
from tkinter.filedialog import askopenfilename
from tkinter import Tk

# Hide Tkinter root window
Tk().withdraw()

# ----------------------------------------------------------
# FUNCTION TO AUTO-LOCATE POPPLER IN EXE + NORMAL PYTHON
# ----------------------------------------------------------
def find_poppler():
    # 1 → When running as EXE (PyInstaller)
    if hasattr(sys, "_MEIPASS"):
        poppler_path = os.path.join(sys._MEIPASS, "poppler", "Library", "bin")
        if os.path.exists(poppler_path):
            return poppler_path

    # 2 → Windows (normal Python)
    possible_paths = [
        r"C:\Users\DELL\Downloads\poppler-25.11.0-0\poppler-25.11.0\Library\bin",
        r"C:\Program Files\poppler\Library\bin",
        r"C:\poppler\Library\bin"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 3 → MacOS (Homebrew)
    mac_path = "/opt/homebrew/bin"
    if sys.platform == "darwin" and os.path.exists(mac_path):
        return mac_path

    # 4 → Linux (default path)
    if sys.platform.startswith("linux"):
        return "/usr/bin"

    return None


POPPLER_PATH = find_poppler()

# Supported file types
SUPPORTED_IMAGE_EXT = [".png", ".jpg", ".jpeg", ".bmp"]
SUPPORTED_EXT = SUPPORTED_IMAGE_EXT + [".pdf", ".txt"]

# Load EasyOCR
reader = easyocr.Reader(['en'])


def extract_text():

    print("Select a file (PDF, PNG, JPG, JPEG, BMP, TXT):")
    file_path = askopenfilename()

    if not file_path:
        print("No file selected.")
        return

    ext = os.path.splitext(file_path)[1].lower()

    # Unsupported file
    if ext not in SUPPORTED_EXT:
        print("Unsupported file type:", ext)
        print("Please choose PDF, image, or TXT.")
        return

    # --------------------------
    # TXT FILE
    # --------------------------
    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            print("\n" + text)
        except Exception as e:
            print("Error reading TXT:", e)
        return

    # --------------------------
    # PDF FILE
    # --------------------------
    if ext == ".pdf":

        if POPPLER_PATH is None:
            print("Poppler not found! PDF reading won't work.")
            return

        print("Converting PDF to images...")

        try:
            pages = convert_from_path(
                file_path,
                dpi=300,
                poppler_path=POPPLER_PATH
            )
        except Exception as e:
            print("Failed to read PDF:", e)
            return

        all_text = []

        for i, page in enumerate(pages):
            temp_img = f"temp_{i}.png"
            page.save(temp_img, "PNG")

            result = reader.readtext(temp_img, detail=0)
            all_text.append("\n".join(result))

            os.remove(temp_img)

        print("\n".join(all_text))
        return

    # --------------------------
    # IMAGE FILE
    # --------------------------
    print("Processing image...")

    try:
        result = reader.readtext(file_path, detail=0)
        print("\n".join(result))
    except Exception as e:
        print("Error processing image:", e)


extract_text()
