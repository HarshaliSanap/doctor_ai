# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pytesseract
from PIL import Image
import re
import os

app = Flask(__name__)
CORS(app)

app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False

model = joblib.load("doctor_model.pkl")

if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

specialist_info = {
    "Cardiology": {
        "en": "A Cardiologist (heart specialist) should be consulted.",
        "hi": "आपको एक कार्डियोलॉजिस्ट (हृदय रोग विशेषज्ञ) से सलाह लेनी चाहिए।",
        "mr": "तुम्ही कार्डिओलॉजिस्ट (हृदयरोग तज्ज्ञ) यांचा सल्ला घ्यावा."
    },
    "Dermatology": {
        "en": "A Dermatologist (skin specialist) should be consulted.",
        "hi": "आपको एक डर्मेटोलॉजिस्ट (त्वचा रोग विशेषज्ञ) से सलाह लेनी चाहिए।",
        "mr": "तुम्ही डर्मेटोलॉजिस्ट (त्वचारोग तज्ज्ञ) यांचा सल्ला घ्यावा."
    },
    "Neurology": {
        "en": "A Neurologist (brain & nervous system specialist) should be consulted.",
        "hi": "आपको एक न्यूरोलॉजिस्ट (मस्तिष्क व तंत्रिका तंत्र विशेषज्ञ) से सलाह लेनी चाहिए।",
        "mr": "तुम्ही न्यूरोलॉजिस्ट (मेंदू व मज्जासंस्था तज्ज्ञ) यांचा सल्ला घ्यावा."
    },
    "Orthopedics": {
        "en": "An Orthopedic specialist (bone & joint specialist) should be consulted.",
        "hi": "आपको एक ऑर्थोपेडिक विशेषज्ञ (हड्डी व जोड़ों के विशेषज्ञ) से सलाह लेनी चाहिए।",
        "mr": "तुम्ही ऑर्थोपेडिक तज्ज्ञ (हाडे व सांधे तज्ज्ञ) यांचा सल्ला घ्यावा."
    },
    "General Medicine": {
        "en": "A General Physician should be consulted.",
        "hi": "आपको एक जनरल फिजिशियन से सलाह लेनी चाहिए।",
        "mr": "तुम्ही जनरल फिजिशियन यांचा सल्ला घ्यावा."
    }
}

DEFAULT_RECOMMENDATION = {
    "en": "Please consult a relevant specialist.",
    "hi": "कृपया संबंधित विशेषज्ञ से सलाह लें।",
    "mr": "कृपया संबंधित तज्ज्ञांचा सल्ला घ्या."
}

SPECIALTY_TRANSLATIONS = {
    "Cardiology": {"en": "Cardiology", "hi": "कार्डियोलॉजी", "mr": "कार्डिओलॉजी"},
    "Dermatology": {"en": "Dermatology", "hi": "डर्मेटोलॉजी", "mr": "डर्मेटोलॉजी"},
    "Neurology": {"en": "Neurology", "hi": "न्यूरोलॉजी", "mr": "न्यूरोलॉजी"},
    "Orthopedics": {"en": "Orthopedics", "hi": "ऑर्थोपेडिक्स", "mr": "ऑर्थोपेडिक्स"},
    "General Medicine": {"en": "General Medicine", "hi": "जनरल मेडिसिन", "mr": "जनरल मेडिसिन"}
}

specialty_keywords = {
    "Cardiology": ["blood count", "cbc", "hemoglobin", "cholesterol", "lipid",
                   "cardiac", "ecg", "ekg", "troponin", "triglyceride", "wbc", "rbc"],
    "Dermatology": ["skin", "biopsy", "dermat", "rash", "lesion"],
    "Neurology": ["brain", "mri brain", "eeg", "neuro", "nerve", "spinal"],
    "Orthopedics": ["bone", "fracture", "joint", "x-ray", "orthop", "spine"],
    "General Medicine": ["general checkup", "fever", "physical examination"]
}

VALUE_PATTERN = re.compile(
    r'([A-Za-z][A-Za-z0-9\s\(\)]*?)\s+([\d]+\.?\d*)\s+([\d]+\.?\d*)\s*-\s*([\d]+\.?\d*)\s*([a-zA-Z/%]+)'
)

TEST_NAME_TRANSLATIONS = {
    "hemoglobin": {"en": "Hemoglobin", "hi": "हीमोग्लोबिन", "mr": "हिमोग्लोबिन"},
    "total rbc count": {"en": "RBC Count", "hi": "आरबीसी काउंट", "mr": "आरबीसी काउंट"},
    "packed cell volume": {"en": "PCV", "hi": "पीसीवी", "mr": "पीसीव्ही"},
    "total wbc count": {"en": "WBC Count", "hi": "डब्ल्यूबीसी काउंट", "mr": "डब्ल्यूबीसी काउंट"},
    "platelet count": {"en": "Platelet Count", "hi": "प्लेटलेट काउंट", "mr": "प्लेटलेट काउंट"},
    "vitamin d": {"en": "Vitamin D", "hi": "विटामिन डी", "mr": "व्हिटॅमिन डी"},
    "vitamin b12": {"en": "Vitamin B12", "hi": "विटामिन बी12", "mr": "व्हिटॅमिन बी12"},
}

STATUS_TEXT = {
    "LOW":    {"en": "is LOW",    "hi": "कम है",      "mr": "कमी आहे"},
    "HIGH":   {"en": "is HIGH",   "hi": "ज़्यादा है",   "mr": "जास्त आहे"},
    "NORMAL": {"en": "is Normal", "hi": "सामान्य है",  "mr": "सामान्य आहे"},
}

OVERALL_MESSAGE = {
    "abnormal": {
        "en": "Some values in your report are outside the normal range.",
        "hi": "आपकी रिपोर्ट में कुछ values सामान्य सीमा से बाहर हैं।",
        "mr": "तुमच्या रिपोर्टमध्ये काही values सामान्य श्रेणीच्या बाहेर आहेत."
    },
    "normal": {
        "en": "All extracted values are within the normal range.",
        "hi": "सभी निकाली गई values सामान्य सीमा के अंदर हैं।",
        "mr": "सर्व काढलेल्या values सामान्य श्रेणीत आहेत."
    },
    "no_data": {
        "en": "Could not reliably extract test values from this image. Please upload a clearer/higher-resolution image.",
        "hi": "इस इमेज से टेस्ट values सही से नहीं निकाली जा सकीं। कृपया एक स्पष्ट / बेहतर गुणवत्ता वाली इमेज अपलोड करें।",
        "mr": "या इमेजमधून टेस्ट values अचूकपणे काढता आल्या नाहीत. कृपया अधिक स्पष्ट / उच्च गुणवत्तेची इमेज अपलोड करा."
    }
}


def preprocess_image_for_ocr(pil_image):
    return pil_image.convert("RGB")


def clean_ocr_text(raw_text):
    text = raw_text.lower()
    text = re.sub(r"[^a-z0-9\s\.\-/%\(\)]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def keyword_based_specialty(clean_text):
    scores = {s: sum(1 for kw in kws if kw in clean_text) for s, kws in specialty_keywords.items()}
    best = max(scores, key=scores.get)
    return best, scores[best]


def extract_test_values(raw_text):
    results = []
    for line in raw_text.split("\n"):
        match = VALUE_PATTERN.search(line)
        if not match:
            continue
        name, result, low, high, unit = match.groups()
        name_clean = re.sub(r"\s+", " ", name).strip()
        try:
            result_f, low_f, high_f = float(result), float(low), float(high)
        except ValueError:
            continue
        if low_f >= high_f:
            continue
        if result_f < low_f:
            status = "LOW"
        elif result_f > high_f:
            status = "HIGH"
        else:
            status = "NORMAL"
        results.append({
            "test_name": name_clean,
            "test_key": name_clean.lower(),
            "result": result_f,
            "reference_low": low_f,
            "reference_high": high_f,
            "unit": unit,
            "status": status
        })
    return results


def build_value_summary(test_results):
    summary = {"en": [], "hi": [], "mr": []}
    for item in test_results:
        if item["status"] == "NORMAL":
            continue
        key = item["test_key"]
        translations = TEST_NAME_TRANSLATIONS.get(key, {
            "en": item["test_name"], "hi": item["test_name"], "mr": item["test_name"]
        })
        status_text = STATUS_TEXT[item["status"]]
        summary["en"].append(f"{translations['en']} {status_text['en']} ({item['result']} {item['unit']}, normal range {item['reference_low']}-{item['reference_high']})")
        summary["hi"].append(f"{translations['hi']} {status_text['hi']} ({item['result']} {item['unit']})")
        summary["mr"].append(f"{translations['mr']} {status_text['mr']} ({item['result']} {item['unit']})")
    return summary


def build_doctor_explanation(test_results):
    explanation = {"en": [], "hi": [], "mr": []}
    for item in test_results:
        key = item["test_key"]
        status = item["status"]
        if key == "hemoglobin" and status == "LOW":
            explanation["en"].append("Your hemoglobin level is low, which may indicate anemia. You may experience weakness, fatigue and dizziness.")
            explanation["hi"].append("आपका हीमोग्लोबिन कम है, जो एनीमिया का संकेत हो सकता है। इससे कमजोरी, थकान और चक्कर आ सकते हैं।")
            explanation["mr"].append("तुमचे हिमोग्लोबिन कमी आहे. हे अशक्तपणाचे लक्षण असू शकते. यामुळे थकवा, कमजोरी आणि चक्कर येऊ शकते.")
        elif key == "total wbc count" and status == "HIGH":
            explanation["en"].append("Your WBC count is elevated, which may indicate an infection or inflammation in the body.")
            explanation["hi"].append("आपका WBC काउंट बढ़ा हुआ है, जो संक्रमण या सूजन का संकेत हो सकता है।")
            explanation["mr"].append("तुमचा WBC काउंट वाढलेला आहे. हे शरीरात संसर्ग किंवा दाह दर्शवू शकते.")
        elif key == "platelet count" and status == "LOW":
            explanation["en"].append("Your platelet count is below normal. This may increase the risk of bleeding.")
            explanation["hi"].append("आपका प्लेटलेट काउंट कम है। इससे रक्तस्राव का खतरा बढ़ सकता है।")
            explanation["mr"].append("तुमचा प्लेटलेट काउंट कमी आहे. यामुळे रक्तस्रावाचा धोका वाढू शकतो.")
        elif key == "vitamin d" and status == "LOW":
            explanation["en"].append("Your Vitamin D level is low. This may cause bone weakness, muscle pain and fatigue.")
            explanation["hi"].append("आपका विटामिन D कम है। इससे हड्डियां कमजोर हो सकती हैं।")
            explanation["mr"].append("तुमचे व्हिटॅमिन D कमी आहे. यामुळे हाडे कमकुवत होऊ शकतात.")
    return explanation


def build_full_trilingual_response(specialty, test_results):
    specialty_name = SPECIALTY_TRANSLATIONS.get(specialty, {"en": specialty, "hi": specialty, "mr": specialty})
    recommendation = specialist_info.get(specialty, DEFAULT_RECOMMENDATION)
    value_summary = build_value_summary(test_results)
    doctor_explanation = build_doctor_explanation(test_results)
    abnormal_count = sum(1 for t in test_results if t["status"] != "NORMAL")
    if not test_results:
        overall_key = "no_data"
    elif abnormal_count > 0:
        overall_key = "abnormal"
    else:
        overall_key = "normal"
    overall = OVERALL_MESSAGE[overall_key]
    result = {}
    for lang in ["en", "hi", "mr"]:
        result[lang] = {
            "specialty": specialty_name[lang],
            "recommendation": recommendation[lang],
            "overall_message": overall[lang],
            "abnormal_values": value_summary[lang],
            "doctor_explanation": doctor_explanation[lang]
        }
    return result, abnormal_count


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    return response


@app.route('/')
def home():
    return "Doctor AI API Running Successfully"


@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    data = request.json
    symptoms = data.get("symptoms", "")
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    try:
        specialty = model.predict([symptoms])[0]
    except Exception as e:
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500
    specialty_name = SPECIALTY_TRANSLATIONS.get(specialty, {"en": specialty, "hi": specialty, "mr": specialty})
    recommendation = specialist_info.get(specialty, DEFAULT_RECOMMENDATION)
    return jsonify({
        "input": symptoms,
        "result": {
            "en": {"specialty": specialty_name["en"], "recommendation": recommendation["en"]},
            "hi": {"specialty": specialty_name["hi"], "recommendation": recommendation["hi"]},
            "mr": {"specialty": specialty_name["mr"], "recommendation": recommendation["mr"]}
        }
    })


@app.route('/predict-report', methods=['POST', 'OPTIONS'])
def predict_report():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    file = request.files['image']
    try:
        image = Image.open(file.stream)
        processed_image = preprocess_image_for_ocr(image)
        text = pytesseract.image_to_string(processed_image, config=r'--oem 3 --psm 6')
        clean_text = clean_ocr_text(text)
        try:
            ml_specialty = model.predict([clean_text])[0]
        except Exception:
            ml_specialty = None
        keyword_specialty, keyword_score = keyword_based_specialty(clean_text)
        if keyword_score >= 2:
            final_specialty = keyword_specialty
        elif ml_specialty:
            final_specialty = ml_specialty
        else:
            final_specialty = keyword_specialty
        test_results = extract_test_values(text)
        trilingual_result, abnormal_count = build_full_trilingual_response(final_specialty, test_results)
        return jsonify({
            "report_text": text,
            "clean_text": clean_text,
            "test_results": test_results,
            "abnormal_count": abnormal_count,
            "result": trilingual_result
        })
    except Exception as e:
        return jsonify({"error": "Report processing failed", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
