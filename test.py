'''import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Adjusting for ambient noise... Please wait.")
    r.adjust_for_ambient_noise(source, duration=1)
    print("Say something:")
    audio = r.listen(source, phrase_time_limit=8)

try:
    print("Recognizing...")
    text = r.recognize_google(audio, language="en-US")
    print("You said:", text)
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError as e:
    print("Could not request results; {0}".format(e))'''


import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator
import pyttsx3
from gtts import gTTS
import os
import tempfile

# Initialize TTS engine (English)
engine = pyttsx3.init()
voices = engine.getProperty("voices")
for voice in voices:
    if "en" in voice.id.lower():
        engine.setProperty("voice", voice.id)
        break

st.title("🎓 KPRIET Campus Voice Assistant (WebApp)")
st.write("🎙️ Speak into your mic → Get navigation help in English, Tamil, and Hindi.")

# --- Record & recognize speech with SpeechRecognition ---
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Adjusting for ambient noise... Please wait.")
        r.adjust_for_ambient_noise(source, duration=1)
        st.info("🎙️ Listening... Speak now (max 8s)")
        audio = r.listen(source, phrase_time_limit=8)

    try:
        st.info("Transcribing with Google API...")
        text = r.recognize_google(audio, language="en-US")
        return text
    except sr.UnknownValueError:
        st.error("❌ Could not understand audio")
        return None
    except sr.RequestError as e:
        st.error(f"❌ API Error: {e}")
        return None

if st.button("🎤 Start Recording"):
    text = recognize_speech()
    if text:
        st.success(f"📝 You said: {text}")

        # --- Location responses (demo) ---
        if "admin" in text.lower():
            response = "Enter through the Security Gate and walk straight. Take the second left — this road leads to the Administrative Block."
        else:
            response = "Sorry, I don't have information about that location yet."

        # --- Translate ---
        tamil_resp = GoogleTranslator(source="en", target="ta").translate(response)
        hindi_resp = GoogleTranslator(source="en", target="hi").translate(response)

        # --- Display ---
        st.markdown(f"**English:** {response}")
        st.markdown(f"**Tamil:** {tamil_resp}")
        st.markdown(f"**Hindi:** {hindi_resp}")

        # --- Speak outputs ---
        # English (pyttsx3, offline)
        engine.say(response)
        engine.runAndWait()

        # Tamil & Hindi speech with gTTS
        for txt, lang, fname in [(tamil_resp, "ta", "ta.mp3"), (hindi_resp, "hi", "hi.mp3")]:
            tts = gTTS(text=txt, lang=lang)
            tts.save(fname)
            st.audio(fname)
            os.remove(fname)
