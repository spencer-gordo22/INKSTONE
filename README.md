# Inkstone

#### Video Demo: https://www.youtube.com/watch?v=APJPQNP7bms

#### Description:

Inkstone is a daily game where you guess a Chinese character. It gives clues about the character’s structure, components, and stroke count. You get six guesses, each guess colors every component by whether it’s in the answer and in the right position, and the game gives hints on guesses four and five. I made it as a way to practice Chinese vocabulary and get more familiar with how characters are put together.

## How to run

Inkstone requires Python 3.9 or newer, Flask, and the CS50 Python library. Open a terminal in the project directory (the folder containing `app.py`) and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sqlite3 inkstone.db < schema.sql
```

The first command creates the virtual environment. If `.venv` already exists, you can skip that command. The last command creates the `inkstone.db` feedback database from `schema.sql`; you only need to run it once. Start the Flask development server from the same project directory with:

```bash
python -m flask --app app run
```

Open the local address printed in the terminal (usually `http://127.0.0.1:5000`) in your browser. To stop the server, press Control-C in the terminal. Guesses come from `data/starter.csv`, and the daily answer is selected from `data/answers.json`. Submitted feedback is saved in `inkstone.db`, the database created from `schema.sql` during setup.

## Design choices

- **Compare on the server:** I chose to compare guesses in Flask because I don’t want the browser to get the answer before the round is over. The browser sends Flask a guess, and `game.py` compares it with the answer and sends feedback back. This keeps the answer out of the browser data until the game ends. It doesn’t hide my source code; it just keeps the answer from being shown early in the game.
- **Represent components as position pairs:** Make Me a Hanzi has the character breakdowns I use. In `game.py`, I pair each component with its position, like left/right or top/bottom. This lets the game tell if a component is in the right spot or if it’s in the character but in another spot. An exact match is green, and a component in the wrong spot is yellow.
- **Use a session counter:** I use Flask’s session to count each browser’s valid guesses. It works a bit like a dictionary: the app saves the count under `visits`, then adds one after each valid guess. The browser sends the session cookie with the next guess, so Flask can pick up the count where it left off. It’s still the same session each time; a guess doesn’t start a new one. The game gives hints on guesses four and five and ends after six guesses.
- **Send guesses without reloading:** In `game.js`, pressing Enter in the board’s input normally triggers the browser’s default Enter behavior. `event.preventDefault()` stops that behavior so the JavaScript can send the guess to Flask with `fetch()` and update the board without reloading the page.
- **Keep the guess list large and answer list small:** Chinese characters can be hard to learn, so I wanted players to be able to guess lots of characters while keeping the daily answer list smaller and picked by me. `starter.csv` has 839 characters, and `answers.json` has 95 answers. I might add levels based on HSK (the Chinese proficiency test) later, but the game doesn’t have levels yet.

## Files

- `app.py` — Flask routes for the game and feedback form. It sends guesses to the game logic and saves feedback to SQLite.
- `game.py` — Loads character records, compares component positions and stroke counts, finds pinyin tones, and chooses the daily answer. Its `__main__` block contains assertion checks.
- `play_terminal.py` — A command-line version of the guessing game that reuses functions from `game.py`.
- `build_db.py` — Currently contains imports only and is not used by the app. I intend to use it to automate preparation of character data from the larger Make Me a Hanzi source.
- `data/starter.csv` — The 839 character records accepted as guesses, with structure, components, pinyin, definition, and stroke count.
- `data/answer_candidates.txt` — A generated list of 700 possible answer candidates that helped me choose the 95 answers in `data/answers.json`.
- `data/answers.json` — The 95 selected characters from which the game chooses its daily answer.
- `schema.sql` — SQL definition for creating the feedback table in a new database.
- `inkstone.db` — SQLite database that stores submitted feedback. It is created from `schema.sql` during setup and is not checked into the repository.
- `requirements.txt` — Python dependencies: `cs50` and `Flask`.
- `templates/layout.html` — Shared HTML page shell, stylesheet, manifest, and JavaScript includes.
- `templates/index.html` — Game board with the guess input in the first cell, feedback form, and answer display elements.
- `static/js/game.js` — Sends guesses and feedback to Flask, then updates the board from the responses.
- `static/js/strings.js` — Defines clue-label strings, which are not currently connected to the page.
- `static/css/style.css` — Page and board styling, feedback colors, cell layout, and flip animation.
- `static/manifest.json` and `static/sw.js` — A minimal manifest and a service-worker placeholder; they do not currently add app functionality.
- `static/icons/.gitkeep` — Keeps the otherwise empty icons directory in the project.
- `data/LICENSE` — A copy of the GNU LGPL v3, which covers `data/starter.csv`.
- `.gitignore` — Excludes the virtual environment, Python cache files, raw source data, local backup files, and the local `inkstone.db` database.
- `CLAUDE.md` — Project notes and development constraints.

## Data sources

Character data comes from [Make Me a Hanzi](https://github.com/skishore/makemeahanzi). Its `dictionary.txt` is licensed under GNU LGPL v3 or later (derived from Unihan and CJKlib), and `graphics.txt` is under the Arphic Public License (derived from Arphic PL KaitiM GB and UKai fonts). `data/starter.csv` is derived from Make Me a Hanzi’s `dictionary.txt` and is distributed under the GNU LGPL v3; a copy of the license is in `data/LICENSE`. The HSK 1–4 lists came from [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) and helped me choose characters.

## AI assistance

I made the game rules and the main comparison logic. I used AI when I had syntax questions and for some other parts of the project. It made the first file skeletons, wrote the `TONE_MARKS` table and assertion checks, and helped with the styling. I made the board cells, feedback colors, and cell font. Claude helped style the rest of the page and add the flip animation. AI also helped process the Make Me a Hanzi and HSK data into the character files, and helped me prepare the app for hosting by setting up the Flask secret key to come from an environment variable. I chose the game design and picked the 95 daily answers. The code comments also say which parts AI helped with.
