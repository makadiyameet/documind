import json
import requests
import re

with open("eval/test_set.json") as f:
    test_cases = json.load(f)

passed = 0

for case in test_cases:
    response = requests.post(
        "http://127.0.0.1:8000/ask",
        json={"text": case["question"]}
    )

    full_text = response.text
    delimiter = "<<<END_SOURCES>>>\n"
    answer = full_text.split(delimiter)[1] if delimiter in full_text else full_text

    def contains_key_terms(expected, actual, threshold=0.6):
        def normalize(text):
            text = text.lower().replace("*", "")
            text = re.sub(r"[-‑]", " ", text)  # replace both regular and special hyphens with space
            text = re.sub(r"[^\w\s]", "", text)  # strip remaining punctuation
            return set(text.split())

        expected_words = normalize(expected)
        actual_words = normalize(actual)
        overlap = expected_words & actual_words
        return len(overlap) / len(expected_words) >= threshold

    is_correct = contains_key_terms(case["expected_answer"], answer)
    if is_correct:
        passed += 1

    print("Q:", case["question"])
    print("Expected:", case["expected_answer"])
    print("Got:", answer.strip())
    print("Pass:", is_correct)
    print("---")

print(f"\n{passed}/{len(test_cases)} passed")