# AI help: Claude created this skeleton file (imports only, no logic) (2026-11-01)
import json
import csv
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

# AI help: Claude made data file paths absolute (based on this file's folder) so they work from any working directory (2026-11-09)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# AI help: Claude wrote the TONE_MARKS table (2026-11-07)
TONE_MARKS = { 
    "ā": 1, "ē": 1, "ī": 1, "ō": 1, "ū": 1, "ǖ": 1,
    "á": 2, "é": 2, "í": 2, "ó": 2, "ú": 2, "ǘ": 2,
    "ǎ": 3, "ě": 3, "ǐ": 3, "ǒ": 3, "ǔ": 3, "ǚ": 3,
    "à": 4, "è": 4, "ì": 4, "ò": 4, "ù": 4, "ǜ": 4,
}

def load_characters():
    characters = {}
    with open(os.path.join(BASE_DIR, "data", "starter.csv"), encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            characters[row["character"]] = row
    return characters


def positional_helper(char_info):
    if char_info["structure"] == "⿱":
        return (char_info["radical_1"], "top"), (char_info["radical_2"], "bottom")
    elif char_info["structure"] == "⿰":
        return (char_info["radical_1"], "left"), (char_info["radical_2"], "right")
    elif char_info["structure"] in {"⿺", "⿵", "⿸", "⿹", "⿷", "⿶", "⿴"}:
        return (char_info["radical_1"], "outer"), (char_info["radical_2"], "inner")
    elif char_info["structure"] == "⿻":
        return (char_info["radical_1"], "inner"), (char_info["radical_2"], "outer")
    else:
        return (char_info["radical_1"], "?"), (char_info["radical_2"], "?")
    
def compare(guess, answer):
    guess_pairs = positional_helper(guess) 
    answer_pairs = positional_helper(answer)
    color_list = []
    answer_radicals = []
    for pairs in answer_pairs:
       answer_radicals.append(pairs[0])
    for pairs in guess_pairs:
        if pairs in answer_pairs:
           color_list.append("green")
        elif pairs[0] in answer_radicals:
            color_list.append("yellow")
        else:
            color_list.append("grey")
    structure_check = (guess["structure"] == answer["structure"])
    stroke_count = int(answer["strokes"]) - int(guess["strokes"])
    return color_list, structure_check, stroke_count
            
def get_tone(pinyin):
    for char in pinyin:
        if char in TONE_MARKS:
            return TONE_MARKS[char]
    return "neutral"

def todays_answer():
    with open(os.path.join(BASE_DIR, "data", "answers.json"), encoding="utf-8") as file:
       char_list = json.load(file)
    now = datetime.now(ZoneInfo("America/New_York"))
    today = now.date()
    days = (today - date(2026, 11, 8)).days
    index = days % len(char_list) 
    todays_word = char_list[index]
    return todays_word

def stroke_display (stroke_difference):
    if stroke_difference > 0:
        return f"+{stroke_difference}⬆"
    elif stroke_difference < 0:
        return f"{stroke_difference}⬇"
    else:
        return "✓"

if __name__ == "__main__":
    # AI help: Claude wrote these test asserts (2026-11-07)
    chars = load_characters()

    # compare: colors, structure, strokes
    results = compare(chars["好"], chars["好"])
    assert results[0] == ["green", "green"], "好 vs 好 colors"
    assert results[1] == True, "好 vs 好 structure"
    assert results[2] == 0, "好 vs 好 strokes"

    results = compare(chars["字"], chars["好"])
    assert results[0] == ["grey", "yellow"], "字 vs 好 colors"
    assert results[1] == False, "字 vs 好 structure"

    results = compare(chars["对"], chars["好"])
    assert results[0] == ["grey", "grey"], "对 vs 好 colors"

    # get_tone
    assert get_tone("hǎo") == 3, "get_tone hao"
    assert get_tone("xiǎo") == 3, "get_tone xiao"
    assert get_tone("de") == "neutral", "get_tone de"

    #last assert written myself Shared radical chars
    results = compare(chars["对"], chars["时"])
    colors, same_structure, stroke_diff = compare(chars["对"], chars["时"])
    assert colors == ["grey", "green"], "对 vs 时 colors"
    assert same_structure == True, "时 vs 对 structure"
    assert stroke_diff == 2, "对 vs 时 strokes" 
    
    print("All tests passed")
    


           
           
           
           
       
       

    
        
            
        
               










    



        







    








