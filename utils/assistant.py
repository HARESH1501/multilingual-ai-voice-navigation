# utils/assistant.py

import whisper
import os
import sounddevice as sd
from scipy.io.wavfile import write
from gtts import gTTS
from playsound import playsound
from googletrans import Translator
from difflib import get_close_matches

# Load model
model = whisper.load_model("base")
translator = Translator()

# Example data (you can modify this)
location_map = {
    "library": {"response": "The library is located near the admin block."},
    "canteen": {"response": "The canteen is behind the auditorium."},
    "auditorium": {"response": "The auditorium is next to the main entrance."},
    "lab": {"response": "The computer lab is on the second floor of CSE block."}
}

synonym_to_key = {
    "library": "library",
    "books": "library",
    "canteen": "canteen",
    "food": "canteen",
    "audi": "auditorium",
    "stage": "auditorium",
    "lab": "lab",
    "computer": "lab"
}

def record_audio(file_path="audio/input.wav", duration=6, fs=44100):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(file_path, fs, recording)
    return file_path

def transcribe_audio(file_path="audio/input.wav"):
    result = model.transcribe(file_path)
    return result["text"].lower()

def translate_text(text, lang_code):
    translated = translator.translate(text, dest=lang_code)
    return translated.text

def fuzzy_location_match(user_text):
    words = user_text.split()
    all_synonyms = list(synonym_to_key.keys())
    for word in words:
        matches = get_close_matches(word, all_synonyms, n=1, cutoff=0.7)
        if matches:
            return synonym_to_key[matches[0]]
    return None

def find_location_response(user_text):
    for syn in synonym_to_key:
        if syn in user_text:
            key = synonym_to_key[syn]
            return location_map[key]["response"]
    fuzzy_key = fuzzy_location_match(user_text)
    if fuzzy_key:
        return location_map[fuzzy_key]["response"]
    return "Sorry, I don't have information about that location yet."
