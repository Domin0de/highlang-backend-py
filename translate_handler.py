import json
from google.cloud import translate_v3 as translate

from .models import OriginalItem, TranslationItem

try:
    with open('lang.json', 'r', encoding='utf-8') as f:
        VALID_LANGUAGES = json.load(f)
except (OSError, json.JSONDecodeError):
    VALID_LANGUAGES = []

def translate_text(text: str, source_lang: str, target_lang: str):
    """Translate the text from the source language to the target language"""

    if source_lang:
        pass
    return


def get_translated(text: str, target_lang: str):
    """Checks DB for existing translation"""

    original = OriginalItem.query.filter(OriginalItem.text == text).first()

    if not original:
        return None

    translation = TranslationItem.query.filter((TranslationItem.lang == target_lang) & (TranslationItem.original_id == original.id)).first()

    return translation
