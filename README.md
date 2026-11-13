# Zimo

https://github.com/user-attachments/assets/04730a77-f56b-426e-bf53-f4cb105e5598

#### Video Demo: https://www.youtube.com/watch?v=APJPQNP7bms

#### Description:

Zimo is a daily game where you guess a Chinese character. It gives clues about the character’s structure, components, and stroke count. You get six guesses, each guess colors every component by whether it’s in the answer and in the right position, and the game gives hints on guesses four and five. I made it as a way to practice Chinese vocabulary and get more familiar with how characters are put together.

## How to play

- Type a Chinese character in the first box and press Enter. On mobile, the handwriting keyboard works well.
- Each guess shows four clues: **structure** (left/right, top/bottom, etc.), **radical 1**, **radical 2**, and **strokes**.
- **Green** means the component is in the answer in the same position. **Yellow** means it’s in the answer but in a different position. **Grey** means it’s not in the answer.
- **Strokes:** `+3` means the answer has 3 more strokes than your guess, `-3` means 3 fewer, and `✓` means they match.
- After guess 4 you get the tone, and after guess 5 you also get the first letter of the pinyin. The game ends after 6 guesses.
- A new character comes out every day at midnight New York time.

## Project structure

```
app.py                 Flask routes: game page, /guess, /feedback
game.py                Game logic: loads characters, compares guesses, picks the daily answer
schema.sql             Feedback table, created automatically at startup
requirements.txt       Python packages (cs50, Flask, gunicorn)
Procfile               Production start command: gunicorn app:app

data/
  starter.csv          839 characters accepted as guesses (structure, components, pinyin, definition, strokes)
  answers.json         95 hand-picked daily answers
  LICENSE              GNU LGPL v3, which covers starter.csv

templates/
  layout.html          Shared page shell (favicon, stylesheet, scripts, GoatCounter analytics)
  index.html           Game board, feedback form, and answer/results card

static/
  css/style.css        Page and board styling, feedback colors, flip animation
  js/game.js           Sends guesses and feedback, updates the board, results sharing, streak stats
  favicon.svg          Browser tab icon
```

## How to run it locally

Zimo needs Python 3.9 or newer. From the project folder, run:

```bash
python3 -m venv .venv          # skip this if .venv already exists
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run
```

Open the address printed in the terminal (usually `http://127.0.0.1:5000`). Press Control-C to stop the server.

To run the logic tests in `game.py`:

```bash
python game.py
```

## Deployment

The `Procfile` starts the app with Gunicorn. Set these environment variables on the host:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Signs session cookies. Use the same value on every instance so games survive restarts. Generate one with `python -c 'import secrets; print(secrets.token_hex(32))'`. If it isn’t set locally, a temporary key is created each time the app starts. |
| `DATABASE_PATH` | Where the feedback database is saved. Point it at a persistent disk so feedback isn’t lost on redeploy. Defaults to `zimo.db` in the project folder. |

## Data and storage

- **Feedback** is saved in a SQLite database (`zimo.db` locally, or `DATABASE_PATH`). The table is created from `schema.sql` if it doesn’t exist. The database is not checked into git.
- **Game progress** for the day (guesses, finished or not) is stored in the Flask session cookie, so the board comes back after a reload.
- **Streaks and stats** are stored in the browser’s `localStorage` under `zimo_stats`. They’re separate for each browser and reset if you clear site data.
  - To test streaks: win a game, open dev tools, set `lastPlayed` to yesterday’s New York date and `currentStreak` to `1`, then reload. The streak should become `2`, and reloading again on the same day shouldn’t count it twice.

## Design choices

- **Compare on the server:** I chose to compare guesses in Flask because I don’t want the browser to get the answer before the round is over. The browser sends Flask a guess, and `game.py` compares it with the answer and sends feedback back. This keeps the answer out of the browser data until the game ends. It doesn’t hide my source code; it just keeps the answer from being shown early in the game.
- **Represent components as position pairs:** Make Me a Hanzi has the character breakdowns I use. In `game.py`, I pair each component with its position, like left/right or top/bottom. This lets the game tell if a component is in the right spot or if it’s in the character but in another spot. An exact match is green, and a component in the wrong spot is yellow.
- **Use a session counter:** I use Flask’s session to count each browser’s valid guesses and keep the board history when the page is reloaded. It works a bit like a dictionary: the app saves the count under `visits`, then adds one after each valid guess. The browser sends the session cookie with the next guess, so Flask can pick up the count and history where it left off. It’s still the same session each time; a guess doesn’t start a new one. The game gives hints on guesses four and five and ends after six guesses. A finished game stays locked until the next day.
- **Send guesses without reloading:** In `game.js`, pressing Enter in the board’s input normally triggers the browser’s default Enter behavior. `event.preventDefault()` stops that behavior so the JavaScript can send the guess to Flask with `fetch()` and update the board without reloading the page.
- **Keep the guess list large and answer list small:** Chinese characters can be hard to learn, so I wanted players to be able to guess lots of characters while keeping the daily answer list smaller and picked by me. `starter.csv` has 839 characters, and `answers.json` has 95 answers. I might add levels based on HSK (the Chinese proficiency test) later, but the game doesn’t have levels yet.

## Data sources

Character data comes from [Make Me a Hanzi](https://github.com/skishore/makemeahanzi). Its `dictionary.txt` is licensed under GNU LGPL v3 or later (derived from Unihan and CJKlib), and `graphics.txt` is under the Arphic Public License (derived from Arphic PL KaitiM GB and UKai fonts). `data/starter.csv` is derived from Make Me a Hanzi’s `dictionary.txt` and is distributed under the GNU LGPL v3; a copy of the license is in `data/LICENSE`. The HSK 1–4 lists came from [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) and helped me choose characters.

## AI assistance

I made the game rules and the main comparison logic. I used AI when I had syntax questions and for some other parts of the project. It made the first file skeletons, wrote the `TONE_MARKS` table and assertion checks, and helped with the styling. I made the board cells, feedback colors, and cell font. Claude helped style the rest of the page and add the flip animation. AI also helped process the Make Me a Hanzi and HSK data into the character files, and helped me prepare the app for hosting by setting up the Flask secret key to come from an environment variable. Claude also helped clean up unused files and reorganize this README. I chose the game design and picked the 95 daily answers. The code comments also say which parts AI helped with.
