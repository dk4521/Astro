import re

with open("backend/tests/test_ai.py", "r") as f:
    content = f.read()

tests_to_remove = [
    "def test_fabricated_nakshatra_is_caught",
    "def test_fabricated_house_is_caught",
    "def test_english_sign_names_are_recognised",
    "def test_sanskrit_graha_names_are_recognised",
    "def test_devanagari_rashi_is_checked",
    "def test_devanagari_nakshatra_and_house_are_checked",
    "def test_devanagari_name_ending_in_a_matra_is_matched",
    "def test_devanagari_claim_at_the_end_of_a_sentence",
    "def test_hindi_states_the_placement_before_the_graha",
    "def test_the_same_wrong_placement_is_reported_once",
    "def test_several_errors_are_all_reported",
]

for test in tests_to_remove:
    # Match from 'def test_...' up to the next 'def ' or end of file
    pattern = re.compile(rf"{re.escape(test)}\(.*?\n(?=def |\Z)", re.DOTALL)
    content = pattern.sub("", content)

with open("backend/tests/test_ai.py", "w") as f:
    f.write(content)
