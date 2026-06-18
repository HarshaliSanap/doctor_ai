"""
Debug script — checks exactly where Hindi/Marathi text gets corrupted:
at the HTTP response level, or later.
"""
import requests

URL = "http://127.0.0.1:5000/predict-report"
IMAGE_PATH = "sample_cbc_report.png"

with open(IMAGE_PATH, "rb") as f:
    files = {"image": f}
    response = requests.post(URL, files=files)

# Check what encoding requests detected
print("Response encoding (requests detected):", response.encoding)
print("Response apparent_encoding:", response.apparent_encoding)
print("Content-Type header:", response.headers.get("Content-Type"))
print()

# Look at the raw bytes for the Hindi specialty word before any JSON parsing
raw_bytes = response.content
print("First 300 raw bytes of response:")
print(raw_bytes[:300])
print()

# Try decoding raw bytes as UTF-8 directly
text_utf8 = raw_bytes.decode("utf-8")
# Find the Hindi specialty value in the raw decoded text
idx = text_utf8.find('"specialty": "')
print("Snippet directly decoded as UTF-8:")
print(text_utf8[idx:idx+60] if idx != -1 else "not found in first pass")