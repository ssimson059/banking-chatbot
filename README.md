# Bank Assistant (BankBot)

Simple domain chatbot. Python (Flask) backend + HTML/CSS/JS frontend.
Uses the Gemini API when a key is set; otherwise it answers from the built-in
keyword FAQ (offline mode), so it works out of the box.

## Run
```
pip install -r requirements.txt
# optional: open .env and paste your Gemini API key
python app.py
```
Open http://127.0.0.1:5000

## Files
- app.py - Flask server, Gemini call and offline fallback
- domain.json - bot name, color, greeting, FAQ and system prompt (edit this to customise)
- static/ - index.html, style.css, script.js
- .env - placeholder, put your own key here (never commit it)
