from flask import Flask, render_template, request, redirect, url_for
from langdetect import detect, DetectorFactory
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

DetectorFactory.seed = 0

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("language-detector-firebase-key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://language-detector-eab83-default-rtdb.firebaseio.com/"
})

# Language Mapping (15+ languages)
lang_map = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh-cn": "Chinese",
    "ja": "Japanese",
    "ar": "Arabic",
    "nl": "Dutch",
    "sq": "Albanian",
    "ko": "Korean",
    "tr": "Turkish"
}

hindi_keywords = ["namaste", "aap", "kaise", "ho","dhanyavaad"]
marathi_keywords = ["namaskar", "kay", "tumhi", "aahat", "challay","kase"]

def detect_language(text):
    text_lower = text.lower()
    words = text_lower.split()

    if any(word in words for word in hindi_keywords):
        return "Hindi"
    if any(word in words for word in marathi_keywords):
        return "Marathi"

    try:
        lang_code = detect(text)
        return lang_map.get(lang_code, f"Other ({lang_code})")
    except:
        return "Could not detect"


# HOME
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    text = ""

    if request.method == "POST":
        text = request.form["text"]
        result = detect_language(text)

        ref = db.reference("history")
        ref.push({
            "text": text,
            "language": result,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return render_template("index.html", result=result, text=text)


#  HISTORY
@app.route("/history")
def history():
    ref = db.reference("history")
    data = ref.get()

    history_list = []
    if data:
        for key, value in data.items():
            value["id"] = key
            history_list.append(value)

        history_list.reverse()

    return render_template("history.html", history=history_list)


#  DELETE SINGLE
@app.route("/delete/<id>")
def delete(id):
    db.reference("history").child(id).delete()
    return redirect(url_for("history"))


#  CLEAR ALL
@app.route("/clear")
def clear():
    db.reference("history").delete()
    return redirect(url_for("history"))


if __name__ == "__main__":
    app.run(debug=True)