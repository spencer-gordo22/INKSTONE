// AI help: Claude created this skeleton file (imports only, no logic) (2026-11-01)
const message_box = document.querySelector("#message")
const input = document.querySelector("#guess_input")
const rows = document.querySelectorAll(".row")
const answer_card = document.querySelector("#answer_card")
const feedback_form = document.querySelector("#feedback_form")
const feedback_text = document.querySelector("#feedback_text")

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
    cell[4].textContent = `${data.stroke_count}${data.stroke_hint}`;

    message_box.textContent = "" || data.hint || data.message;
    row++;
    input.value = "";

    if (data.game_over || row >= rows.length) {
        input.remove();
        answer_card.textContent = `${data.answer_info.character} ${data.answer_info.pinyin} ${data.answer_info.defintion}`;
        answer_card.hidden = false;
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
