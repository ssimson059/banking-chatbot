import os, re, json
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()
BASE = Path(__file__).parent
CFG = json.loads((BASE / "domain.json").read_text(encoding="utf-8"))

app = Flask(__name__, static_folder="static", static_url_path="")
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()


def local_answer(message: str) -> str:
    """Offline fallback: pick the FAQ entry with the most keyword hits."""
    text = message.lower()
    best, best_score = None, 0
    for item in CFG["faq"]:
        score = sum(1 for k in item["keywords"] if k in text)
        if score > best_score:
            best, best_score = item, score
    return best["answer"] if best else CFG["fallback"]


def gemini_answer(message: str, history: list) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    contents = []
    for turn in history[-10:]:
        role = "user" if turn.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": str(turn.get("text", ""))}]})
    contents.append({"role": "user", "parts": [{"text": message}]})
    body = {
        "systemInstruction": {"parts": [{"text": CFG["system_prompt"]}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 600},
    }
    r = requests.post(url, headers={"x-goog-api-key": API_KEY}, json=body, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/config")
def config():
    return jsonify({k: CFG[k] for k in ("name", "bot", "color", "greeting", "chips")})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []
    if not message:
        return jsonify({"error": "Message is empty."}), 400
    if API_KEY:
        try:
            return jsonify({"reply": gemini_answer(message, history), "source": "gemini"})
        except Exception as exc:  # fall back to local answers
            print("Gemini error:", exc)
    return jsonify({"reply": local_answer(message), "source": "local"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
