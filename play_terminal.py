# AI help: Claude created this skeleton file (imports only, no logic) (2026-11-01)
import game
from game import load_characters, compare, get_tone, stroke_display
import random

full_list = load_characters()

chars = list(full_list)
answer = random.choice(chars)
answer_row = full_list[answer]

for i in range (6):
    guess = input("Guess: ")
    while guess not in chars:
            print("Not in the list.")
            guess = input("Guess: ")
    tone = get_tone(answer_row["pinyin"])
    first_char = answer_row["pinyin"][0]
    guess_row = full_list[guess]
    results = compare(guess_row, answer_row)
    stroke_difference = stroke_display(results[2])
    print(stroke_difference)
    print(results)
    if guess == answer:
        print("Congrats, you won!")
        break
    if i == 3:
         print("Hint: The tone is", tone)
    if i == 4:
        print("Hint: The first letter of it's pinyin is:", first_char)
else:
    print("Sorry, you lost. The answer was", answer)
