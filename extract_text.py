import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open("CBC report.png")

# Image मोठी करा
w, h = img.size
img = img.resize((w * 4, h * 4))

# Grayscale
img = img.convert("L")

text = pytesseract.image_to_string(img, config="--psm 6")

print("===== REPORT TEXT =====")
print(text)