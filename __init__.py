import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from google.cloud import translate_v3 as translator, texttospeech_v1 as tts

from .translate_handler import translate_text, VALID_LANGUAGES
from .helper import validate_translate_req

load_dotenv('.env')
CONNECTION_STRING = f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@localhost:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION_STRING
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

translation_client = translator.TranslationServiceClient(
    client_options={"api_key": os.environ.get('GOOGLE_API_KEY')}
)

tts_client = tts.TextToSpeechClient(
    client_options={"api_key": os.environ.get('GOOGLE_API_KEY')}
)

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
