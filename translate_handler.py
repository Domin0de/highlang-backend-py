import os
import json
import uuid

from google.cloud import translate_v3 as translator, texttospeech_v1 as tts

from . import db, translation_client, tts_client
from .models import OriginalItem, TranslationItem

try:
    with open('lang.json', 'r', encoding='utf-8') as f:
        VALID_LANGUAGES = json.load(f)
except (OSError, json.JSONDecodeError):
    VALID_LANGUAGES = []

PROJECT_STRING = os.environ.get('PROJECT_STRING')

def translate_text(text: str, target_lang: str):
    """Translate the text from the source language to the target language"""

    translated = get_translated(text, target_lang)

    if not translated:
        translated = get_combined(text, target_lang)
    
    if not translated:
        translated = translate_text_api(text, target_lang)

    try:
        with open(f'audio/{translated.audio_id}.mp3', 'rb') as f:
            audio_bytes = f.read()
    except (OSError, AttributeError):
        return {
            "status": "success",
            "translation": translated.html_text,
            "audio": None
        }

    return {
        "status": "success",
        "translation": translated.html_text,
        "audio": audio_bytes
    }

def get_translated(text: str, target_lang: str):
    """Checks DB for existing translation"""

    original = db.session.query(OriginalItem).filter(OriginalItem.text == text).first()

    if not original:
        return None

    translation = db.session.query(TranslationItem).filter(
        TranslationItem.lang == target_lang,
        TranslationItem.original_id == original.id
    ).first()

    return translation

def get_combined(text: str, target_lang: str):
    """Try cobble together a translation from existing translations"""

    words = text.split()

    if len(words) < 2:
        return None

    translation = []

    for word in words:
        original = db.session.query(OriginalItem).filter(OriginalItem.text == word).first()

        if not original:
            break

        translation_item = db.session.query(TranslationItem).filter(
            TranslationItem.lang == target_lang,
            TranslationItem.original_id == original.id
        ).first()

        if not translation_item:
            break

        translation.append(translation_item)

    if len(translation) == len(words):
        return translation

    return None

def get_audio(translated_text: str, language: str):
    """Get the audio for the translation"""
    tts_text = tts.SynthesisInput(text=translated_text)
    tts_voice = tts.VoiceSelectionParams(language_code=language)
    tts_audio_conf = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

    tts_req = tts.SynthesizeSpeechRequest(
        input=tts_text,
        voice=tts_voice,
        audio_config=tts_audio_conf
    )

    tts_res = tts_client.synthesize_speech(request=tts_req)

    tts_id = str(uuid.uuid4())

    audio_path = f"audio/{tts_id}.mp3"

    with open(audio_path, 'wb') as f:
        f.write(tts_res.audio_content)

    return tts_id

def translate_text_api(text: str, target_lang: str):
    """Translate the text using the Google Translate API"""

    translation_req = translator.TranslateTextRequest(
        parent=PROJECT_STRING,
        contents=[text],
        target_language_code=target_lang,
        mime_type='text/plain'
    )

    translation_res = translation_client.translate_text(request=translation_req)

    if not translation_res.translations:
        return {"status": "error", "message": "Translation failed"}
    
    translated_text = translation_res.translations[0].translated_text

    romanised_req = translator.TranslateTextRequest(
        parent=PROJECT_STRING,
        contents=[translated_text],
        target_language_code='en',
        mime_type='text/plain'
    )

    romanised_res = translation_client.romanize_text(request=romanised_req)

    if not romanised_res.translations:
        return {"status": "error", "message": "Romanisation failed"}

    romanised_text = romanised_res.romanizations[0].romanized_text

    html_text = f"<p>{translated_text}</p><p><i>{romanised_text}</i></p>"

    audio_id = get_audio(translated_text)

    original = OriginalItem(text=text)
    db.session.add(original)

    translation = TranslationItem(
        lang=target_lang,
        html_text=html_text,
        original_id=original.id,
        audio_id=audio_id
    )

    db.session.add(translation)
    db.session.commit()

    return translation
