import pytesseract
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

image_path = "CBC report.png"

img = Image.open(image_path)

w, h = img.size
img = img.resize((w * 4, h * 4))
img = img.convert("L")

text = pytesseract.image_to_string(img, config="--psm 6")

print("===== OCR TEXT =====")
print(text)

# Report type detection
if "blood count" in text.lower() or "cbc" in text.lower():
    report_type = "CBC"
else:
    report_type = "Unknown"

print("\nDetected Report Type:", report_type)
# Specialty recommendation

if report_type == "CBC":
    specialty = "General Medicine"

    doctors = [
        "Dr. Meera Rao",
        "Dr. Rajesh Kumar"
    ]

    print("\nRecommended Specialty:", specialty)

    print("\nRecommended Doctors:")
    for doctor in doctors:
        print("-", doctor)