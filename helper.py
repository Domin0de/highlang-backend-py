from flask import Request

from .translate_handler import VALID_LANGUAGES

def validate_translate_req(req: Request):
    """Validates the translation request arguments"""

    text = req.args.get('text')
    source_lang = req.args.get('src')
    target_lang = req.args.get('target')

    if not text:
        return {"status": "error", "message": "No text provided"}
    if not target_lang:
        return {"status": "error", "message": "No target language provided"}

    if source_lang and source_lang not in VALID_LANGUAGES:
        return {"status": "error", "message": "Invalid source language"}
    if target_lang not in VALID_LANGUAGES:
        return {"status": "error", "message": "Invalid target language"}

    return {"status": "success", "data": (text, source_lang, target_lang)}
