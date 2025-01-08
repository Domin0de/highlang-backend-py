from flask import Flask, Request, request, jsonify

from .translate_handler import translate, VALID_LANGUAGES
from .helper import validate_translate_req

app = Flask(__name__)

# ----------------------------------- ROUTES -----------------------------------

@app.route('/api/v1/translate', methods=['GET'])
def get_translate():
    """Return the handled translation for the provided text"""

    args = validate_translate_req(request)

    if args["status"] == "error":
        return jsonify(args), 400

    text, source_lang, target_lang = args["data"]

    translation = translate(text, source_lang, target_lang)

    if translation['status'] == 'error':
        return jsonify(translation), 400

    return jsonify(translation)

@app.route('/api/v1/languages', methods=['GET'])
def get_languages():
    """Return the supported languages"""
    return jsonify({"status": "success", "languages": VALID_LANGUAGES})
