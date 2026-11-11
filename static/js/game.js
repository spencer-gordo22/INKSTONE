// AI help: Claude created this skeleton file (imports only, no logic) (2026-11-01)
const message_box = document.querySelector("#message")
const input = document.querySelector("#guess_input")
const rows = document.querySelectorAll(".row")
const answer_card = document.querySelector("#answer_card")
const feedback_form = document.querySelector("#feedback_form")
const feedback_text = document.querySelector("#feedback_text")
const initial_state = JSON.parse(document.querySelector("#initial_game_state").textContent)
const share = document.querySelector("#share_results")

let row = 0;

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.isComposing) {
        event.preventDefault();
        submit_guess();
    }
});

async function submit_guess() {
    const guess = input.value.trim();
    if (guess === "") {
        rows[row].classList.add("shake");
        setTimeout(() => {
            rows[row].classList.remove("shake");
        }, 400);
        return;
    }

    const response = await fetch("/guess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ guess: guess})
    });
    const data = await response.json();
    console.log(data);

    if (!data.colors) {
        message_box.textContent = data.message;
        rows[row].classList.add("shake");
        setTimeout(() => {
            rows[row].classList.remove("shake");
        }, 400);
        return;
    }

    const current_row = rows[row]

    const cell = current_row.querySelectorAll(".cell")

    cell[0].textContent = data.guess
    cell[1].textContent = data.same_structure ? "✅" : "❌";
    cell[2].textContent = data.parts[0]
    cell[2].classList.add(data.colors[0])
    cell[3].textContent = data.parts[1]
    cell[3].classList.add(data.colors[1])
    cell[4].textContent = data.stroke_hint;

    message_box.textContent = data.hint || data.message || "";
    row++;
    input.value = "";

    if (data.game_over || row >= rows.length) {
        input.remove();
        message_box.textContent = data.message;
        answer_card.hidden = false;
        share.hidden = false;
        if (data.answer_info) {
            document.querySelector("#answer_hanzi").textContent = data.answer_info.character || "";
            document.querySelector("#answer_pinyin").textContent = data.answer_info.pinyin || "";
            document.querySelector("#answer_english").textContent = data.answer_info.definition || data.answer_info.defintion || "";
        }
        const won = Boolean(data.message && data.message.toLowerCase().includes("congrats"));
        if (won) message_box.textContent = "";
        handleGameEnd(won);
        if (won) celebrate(true);
        return;
    }

    // Move the input box down into the next row's guess cell
    rows[row].querySelector(".cell").appendChild(input);
    input.focus();
}

feedback_form.addEventListener("submit", async (event) => {
    event.preventDefault()
    
    const response = await fetch ("/feedback", {
        method: "POST",
        headers: {"Content-Type": "application/json" },
        body: JSON.stringify({ message: feedback_text.value}),
    })
    const reply = await response.json();

    if (reply.ok) {
        message_box.textContent = "Thanks!";
    }
    else {
        message_box.textContent = reply.message;
    }

});

function redraw_history(history, finished = false) {
    if (!history || history.length === 0) return;

    for (let i = 0; i < history.length && i < rows.length; i++) {
        const data = history[i];
        const cells = rows[i].querySelectorAll(".cell");

        cells[0].textContent = data.guess;
        cells[1].textContent = data.same_structure ? "✅" : "❌";
        cells[2].textContent = data.parts[0];
        cells[2].classList.add(data.colors[0]);
        cells[3].textContent = data.parts[1];
        cells[3].classList.add(data.colors[1]);
        cells[4].textContent = data.stroke_hint;
    }

    row = history.length;
    if (!finished && row < rows.length) {
        rows[row].querySelector(".cell").appendChild(input);
        input.focus();
    }
}

// Restore the board from the session when the player reloads the page.
redraw_history(initial_state.history, initial_state.finished);

const copy_toast = document.querySelector("#copy_toast");
let copy_toast_timer;

function show_copy_toast() {
    copy_toast.classList.add("show");
    clearTimeout(copy_toast_timer);
    copy_toast_timer = setTimeout(() => copy_toast.classList.remove("show"), 1800);
}

share.addEventListener("click", async () => {
    const symbols = { green: "🟩", yellow: "🟨", grey: "⬛" };
    const results = [`Zimo ${row}/6`];
    for (let i = 0; i < row; i++) {
        const cells = rows[i].querySelectorAll(".cell");
        const color1 = ["green", "yellow", "grey"].find(color => cells[2].classList.contains(color));
        const color2 = ["green", "yellow", "grey"].find(color => cells[3].classList.contains(color));
        results.push((symbols[color1] || "⬛") + (symbols[color2] || "⬛"));
    }
    try {
        await navigator.clipboard.writeText(results.join("\n"));
        show_copy_toast();
    } catch {
        message_box.textContent = "Could not copy results on this browser.";
    }
});

// --- Streak + Stats (localStorage) ---
const STATS_KEY = "zimo_stats";

function loadStats() {
  const defaults = {
    currentStreak: 0,
    maxStreak: 0,
    gamesPlayed: 0,
    gamesWon: 0,
    lastPlayed: null
  };
  try {
    const raw = localStorage.getItem(STATS_KEY);
    if (!raw) return defaults;
    const stats = JSON.parse(raw);
    return stats && typeof stats === "object" ? { ...defaults, ...stats } : defaults;
  } catch {
    return defaults;
  }
}

function saveStats(stats) {
  try {
    localStorage.setItem(STATS_KEY, JSON.stringify(stats));
  } catch {
    // Keep the game-over screen available when browser storage is unavailable.
  }
}

function updateStats(won) {
  const stats = loadStats();
  const today = gameDate();
  const yesterday = shiftGameDate(today, -1);

  // Only count once per day
  if (stats.lastPlayed === today) return stats;

  stats.gamesPlayed++;
  if (won) {
    stats.gamesWon++;
    if (stats.lastPlayed === yesterday) {
      stats.currentStreak++;
    } else {
      stats.currentStreak = 1;
    }
    stats.maxStreak = Math.max(stats.maxStreak, stats.currentStreak);
  } else {
    stats.currentStreak = 0;
  }
  stats.lastPlayed = today;
  saveStats(stats);
  return stats;
}

function showStats(stats) {
  document.querySelector("#streak").textContent = stats.currentStreak;
  document.querySelector("#max_streak").textContent = stats.maxStreak;
  document.querySelector("#played").textContent = stats.gamesPlayed;
  document.querySelector("#wins").textContent = stats.gamesWon;
  document.querySelector("#stats").hidden = false;
  document.querySelector("#next_game_note").hidden = false;
  view_puzzle.hidden = false;
}

function gameDate(date = new Date()) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day}`;
}

function shiftGameDate(dateString, days) {
  const [year, month, day] = dateString.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day + days)).toISOString().slice(0, 10);
}

// Win celebration: banner on the card, plus a confetti burst when the win just happened
function celebrate(live) {
  document.querySelector("#win_banner").hidden = false;
  answer_card.classList.add("won");
  if (!live || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const pieces = ["🎉", "✨", "🎊", "⭐", "💚", "🔥", "🥳"];
  const colors = ["#6ee79a", "#3fb970", "#ffd166", "#ff6b9a", "#7cc4ff", "#c792ff"];
  const layer = document.createElement("div");
  layer.className = "confetti_layer";
  for (let i = 0; i < 70; i++) {
    const bit = document.createElement("span");
    bit.className = "confetti";
    if (i % 3 === 0) {
      bit.textContent = pieces[i % pieces.length];
    } else {
      bit.classList.add("confetti_bit");
      bit.style.background = colors[i % colors.length];
    }
    bit.style.left = `${Math.random() * 100}vw`;
    bit.style.setProperty("--drift", `${(Math.random() - 0.5) * 200}px`);
    bit.style.setProperty("--spin", `${(Math.random() - 0.5) * 1080}deg`);
    bit.style.animationDuration = `${2.2 + Math.random() * 1.8}s`;
    bit.style.animationDelay = `${Math.random() * 0.6}s`;
    layer.appendChild(bit);
  }
  document.body.appendChild(layer);
  setTimeout(() => layer.remove(), 5000);
}

// "View your puzzle" hides the card; "Show results" brings it back
const view_puzzle = document.querySelector("#view_puzzle")
const show_results = document.querySelector("#show_results")

view_puzzle.addEventListener("click", () => {
  answer_card.hidden = true;
  show_results.hidden = false;
});

show_results.addEventListener("click", () => {
  answer_card.hidden = false;
  show_results.hidden = true;
});

// Call this when the game ends
function handleGameEnd(won) {
  const stats = updateStats(won);
  showStats(stats);
}

if (initial_state.finished) {
    input.remove();
    message_box.textContent = initial_state.message;
    answer_card.hidden = false;
    share.hidden = false;
    if (initial_state.answer_info) {
        document.querySelector("#answer_hanzi").textContent = initial_state.answer_info.character || "";
        document.querySelector("#answer_pinyin").textContent = initial_state.answer_info.pinyin || "";
        document.querySelector("#answer_english").textContent = initial_state.answer_info.definition || initial_state.answer_info.defintion || "";
    }
    const won = Boolean(initial_state.message && initial_state.message.toLowerCase().includes("congrats"));
    if (won) message_box.textContent = "";
    handleGameEnd(won);
    if (won) celebrate(false);
}
