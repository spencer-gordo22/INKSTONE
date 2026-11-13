# AI help: Claude created this skeleton file (imports only, no logic) (2026-11-01)
import os
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from game import compare, load_characters, todays_answer, get_tone, stroke_display
from datetime import date, datetime
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = os.environ.get("DATABASE_PATH")
if env: 
    DB_PATH = env 
else: 
    DB_PATH = os.path.join(BASE_DIR, "zimo.db")


def initialize_database(database_path=DB_PATH):
    with sqlite3.connect(database_path) as connection:
        with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())


initialize_database()
db = SQL("sqlite:///" + DB_PATH)


app = Flask(__name__)
# Use a fresh key for local development if no persistent deployment key is configured.
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)
all_chars = load_characters()


def reset_daily_session():
    today = datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    if session.get("date") != today:
        session["date"] = today
        session["visits"] = 0
        session["finished"] = False
        session["history"] = []
        session.pop("answer_info", None)
        session.pop("game_message", None)


@app.route('/', methods = ['POST', 'GET'])
def homepage():
    reset_daily_session()
    return render_template(
        "index.html",
        session_history=session.get("history", []),
        game_finished=session.get("finished", False),
        answer_info=session.get("answer_info"),
        game_message=session.get("game_message", ""),
    )

@app.route('/guess', methods=['POST'])
def guess():
    if request.method == 'POST':
        guess_data = request.get_json(silent=True)
        if not isinstance(guess_data, dict) or not isinstance(guess_data.get("guess"), str):
            return jsonify({"message": "Please send a guess as JSON."}), 400
        word = guess_data["guess"]

        reset_daily_session()
        if session.get("finished", False):
            return jsonify ({
                "message": "Thanks for playing! Please come back tomorrow."
            })
        if "history" not in session:
            session["history"] = []
        answer = todays_answer()
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
                message = "Congrats, you won!"
                session["finished"] = True
                game_over = True
            elif guess_count == 6:
                message = f"You lost. The answer was: {answer}"
                session["finished"] = True
                game_over = True
            if not game_over and guess_count >= 4:
                hint = f"The tone is: {tone}"
                if guess_count >= 5:
                    hint += f". Pinyin starts with: {first_char}"
            if game_over:
                answer_info = answer_row
                session["answer_info"] = answer_row
                session["game_message"] = message
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
    feedback_data = request.get_json(silent=True)
    if not isinstance(feedback_data, dict) or not isinstance(feedback_data.get("message"), str):
        return jsonify({"message": "Please send feedback as JSON."}), 400
    message = feedback_data["message"]
    if not message or len(message) > 1000:
        return jsonify ({
            "message": "Please write between 1 and 1000 characters."
        })
    db.execute("INSERT INTO feedback (message) VALUES (?)", message)
    return jsonify ({
        "ok": True
    })



        
