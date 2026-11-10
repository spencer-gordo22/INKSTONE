# AI help: Claude created this skeleton file (imports only, no logic) (2026-11-01)
import os
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from game import compare, load_characters, todays_answer, get_tone, stroke_display
from datetime import date, datetime
from zoneinfo import ZoneInfo

# AI help: Claude made the DB path absolute (based on this file's folder) so the app runs from any working directory (2026-11-09)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = SQL("sqlite:///" + os.path.join(BASE_DIR, "inkstone.db"))


app = Flask(__name__)
# AI help: Claude changed the secret key to read from the SECRET_KEY env variable, with a dev-only fallback (2026-11-09)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-not-secret")
all_chars = load_characters()


@app.route('/', methods = ['POST', 'GET'])
def homepage():
    return render_template("index.html")

@app.route('/guess', methods=['GET', 'POST'])
def guess():
    if request.method == 'POST':
        now = datetime.now(ZoneInfo("America/New_York"))
        today = now.date()
        today = today.isoformat()
        if session.get("date", None) != today:
            session["date"] = today
            session["visits"] = 0
            session["finished"] = False
        if session.get("finished", False):
            return jsonify ({
                "message": "Thanks For playing, Please come back tommorow!"
            })
        if "history" not in session:
            session["history"] = []
        answer = todays_answer()
        guess1 = request.get_json()
        word = guess1["guess"]
        if word in all_chars:
            guess_count = session.get("visits", 0) + 1
            session["visits"] = guess_count
            hint = None
            answer_info = None
            message = None
            game_over = False
            guess_row = all_chars[word]
            answer_row = all_chars[answer]
            results = compare(guess_row, answer_row)
            stroke_difference = stroke_display(results[2])
            first_char = answer_row["pinyin"][0]
            tone = get_tone(answer_row["pinyin"])
            if word == answer:
                message = "Congrats you won!"
                session["finished"] = True
                game_over = True
            elif guess_count == 6:
                message = f"You lost. The answer was: {answer}"
                session["finished"] = True
                game_over = True
            if not game_over:
                if guess_count == 4:
                    hint = f"The tone is: {tone}"
                if guess_count == 5:
                    hint = f"Pinyin starts with: {first_char}"
            if game_over:
                answer_info = answer_row
            session["history"].append ({
                "guess": word,
                "same_structure": results[1],
                "parts": [guess_row["radical_1"], guess_row["radical_2"]],
                "colors": results[0],
                "stroke_count": guess_row["strokes"],
                "stroke_hint": stroke_difference,
            })
            session.modified = True
            return jsonify({
                "hint": hint,
                "message": message,
                "stroke_hint": stroke_difference,
                "colors": results[0],
                "same_structure": results[1],
                "guess": word,
                "game_over": game_over,
                "parts": [guess_row["radical_1"], guess_row["radical_2"]],
                "stroke_count": guess_row["strokes"],
                "answer_info": answer_info,
                "session_history": session["history"],
            })
        else:
            return jsonify ({
                "message": "Not in the list of allowed guesses",
            })
    return render_template("index.html")


@app.route('/feedback', methods = ['POST'])
def reviews():
    feedback_text = request.get_json()
    message = feedback_text["message"]
    if not message or len(message) > 1000:
        return jsonify ({
            "message": "Please write between 1 and 1000 characters."
        })
    db.execute("INSERT INTO feedback (message) VALUES (?)", message)
    return jsonify ({
        "ok": True
    })



        
