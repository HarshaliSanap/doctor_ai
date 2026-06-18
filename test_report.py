import requests
import json

URL = "http://127.0.0.1:5000/predict-report"
IMAGE_PATH = "sample_cbc_report.png"

try:
with open(IMAGE_PATH, "rb") as f:
files = {"image": f}

```
    response = requests.post(URL, files=files)

data = response.json()

print("\n==============================")
print("      AI HEALTH REPORT")
print("==============================\n")

result = data["result"]

# English Output
en = result["en"]

print("Recommended Specialty:")
print(en["specialty"])

print("\nDetected Issues:")

for issue in en["abnormal_values"]:
    print("•", issue)

if "doctor_explanation" in en:
    print("\nDoctor Analysis:")

    if isinstance(en["doctor_explanation"], list):
        for item in en["doctor_explanation"]:
            print("-", item)
    else:
        print(en["doctor_explanation"])

print("\nOverall Message:")
print(en["overall_message"])

print("\nRecommendation:")
print(en["recommendation"])

print("\n==============================\n")

# Save response
with open(
    "response_clean.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Saved clean output to response_clean.json")
```

except Exception as e:
print("Error:", e)
