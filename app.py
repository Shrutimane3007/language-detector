from flask import Flask, render_template, request, jsonify
from langdetect import detect
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate(".gitignore/language-detector-firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Language mapping (with Marathi)
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese",
    "ar": "Arabic"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect_language():
    text = request.json["text"]

    try:
        code = detect(text)
        language = LANGUAGES.get(code, code)
    except:
        language = "Could not detect"

    # Save to Firebase
    db.collection("results").add({
        "text": text,
        "language": language
    })

    return jsonify({
        "language": language,
        "message": "Result saved successfully!"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)