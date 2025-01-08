import json

try:
    with open('lang.json', 'r', encoding='utf-8') as f:
        VALID_LANGUAGES = json.load(f)
except (OSError, json.JSONDecodeError):
    VALID_LANGUAGES = []

def translate(text: str, source_lang: str, target_lang: str):
    return
