import os

from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from dotenv import load_dotenv

from .translate_handler import translate_text, VALID_LANGUAGES
from .helper import validate_translate_req

load_dotenv('.env')
CONNECTION_STRING = f"mysql+mysqlconnector://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"

app = Flask(__name__)

sql_engine = create_engine(CONNECTION_STRING)

# ----------------------------------- ROUTES -----------------------------------

@app.route('/api/v1/translate', methods=['GET'])
def get_translate():
    """Return the handled translation for the provided text"""

    args = validate_translate_req(request)

    if args["status"] == "error":
        return jsonify(args), 400

    text, source_lang, target_lang = args["data"]

    translation = translate_text(text, source_lang, target_lang)

    if translation['status'] == 'error':
        return jsonify(translation), 400

    return jsonify(translation)

@app.route('/api/v1/languages', methods=['GET'])
def get_languages():
    """Return the supported languages"""
    return jsonify({"status": "success", "languages": VALID_LANGUAGES})
