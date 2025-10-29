# app.py
import streamlit as st
import whisper
import sounddevice as sd
from scipy.io.wavfile import write
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile, os, time
from difflib import get_close_matches
import numpy as np
import base64
import streamlit.components.v1 as components

# ----------------------------
# Configuration
# ----------------------------
FS = 44100
DURATION = 5  # seconds to record
AUDIO_FILE = "input.wav"

st.set_page_config(page_title="KPRIET Campus Voice Assistant", page_icon="🎓", layout="centered")

# ----------------------------
# Location Map
# ----------------------------
location_map = {
    "admin": {"synonyms": ["admin", "admission office", "main block", "admin block"],
              "response": "Enter through the Security Gate and walk straight along the main road. Take the second left — this road leads to the Administrative Block."},
    "mechanical": {"synonyms": ["mechanical", "mechanical block"],
                   "response": "Walk in through the Security Gate. Take the second left — you’ll see the Admin Block on your right. Keep walking straight, pass the Main Block. Then take a right turn. You’ll reach the Mechanical Block at the end of the road."},
    "cse": {"synonyms": ["cse", "cse block"],
            "response": "Enter through the Security Gate and walk straight. You’ll see the Imperial Hall on your right. Walk past the Imperial Hall — you’ll find a pathway beside it. Take that pathway — it will lead you to the Main Block. Walk straight past the Main Block. Continue straight until you see the pond. Cross the pond area and keep walking. Pass the Open-Air Theatre, then take a left turn. The CSE Block will be on your right side."},
    "library": {"synonyms": ["library", "central library"],
                "response": "Enter through the Security Gate and walk straight. Keep walking on the main road. Take the small right near the Girls Washroom. Keep walking and you’ll see the library on your right."},
    "food court": {"synonyms": ["food court"],
                   "response": "Enter through the Security Gate and walk straight. Just after the parking area, you will see the Food Court on your left."}
}

# flatten synonyms -> key mapping
synonym_to_key = {syn.lower(): key for key, val in location_map.items() for syn in val["synonyms"]}

# ----------------------------
# Helper functions
# ----------------------------
def fuzzy_location_match(user_text):
    words = user_text.split()
    all_synonyms = list(synonym_to_key.keys())
    for word in words:
        matches = get_close_matches(word, all_synonyms, n=1, cutoff=0.7)
        if matches:
            return synonym_to_key[matches[0]]
    return None

def find_location_response(transcribed_text):
    if not transcribed_text:
        return "Sorry, I don't have information about that location yet."
    text = transcribed_text.lower()
    for syn in synonym_to_key:
        if syn in text:
            return location_map[synonym_to_key[syn]]["response"]
    fuzzy = fuzzy_location_match(text)
    if fuzzy:
        return location_map[fuzzy]["response"]
    return "Sorry, I don't have information about that location yet."

# ----------------------------
# Recording
# ----------------------------
def record_audio(filename=AUDIO_FILE, duration=DURATION, fs=FS):
    st.info("🎙️ Recording... Please speak now.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    # Save WAV
    write(filename, fs, recording)
    st.success("✅ Recording complete.")
    time.sleep(0.2)

# ----------------------------
# Whisper model load (cached)
# ----------------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

# ----------------------------
# Translation helper
# ----------------------------
def translate_text(text, lang_code):
    try:
        translator = GoogleTranslator(source="auto", target=lang_code)
        return translator.translate(text)
    except Exception:
        return "Translation unavailable."

# ----------------------------
# TTS: generate mp3 bytes with gTTS then return base64 string
# ----------------------------
def tts_to_b64(text, lang):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            fname = tmp.name
        # gTTS saves to file
        gTTS(text=text, lang=lang).save(fname)
        # read bytes and base64-encode
        with open(fname, "rb") as f:
            b = f.read()
        b64 = base64.b64encode(b).decode("utf-8")
        # cleanup file
        try:
            os.remove(fname)
        except:
            pass
        return b64
    except Exception as e:
        # return None on failure
        print("TTS error:", e)
        return None

# ----------------------------
# Play three audios sequentially in browser using data URIs
# ----------------------------
def play_three_in_browser(b64_en, b64_ta, b64_hi):
    # Build HTML with audio tags and sequential play script
    # Use small invisible audio players; autoplay starts the chain.
    html = f"""
    <div id="players" style="display:none">
      <audio id="a1" src="data:audio/mp3;base64,{b64_en}"></audio>
      <audio id="a2" src="data:audio/mp3;base64,{b64_ta}"></audio>
      <audio id="a3" src="data:audio/mp3;base64,{b64_hi}"></audio>
    </div>
    <script>
      const a1 = document.getElementById("a1");
      const a2 = document.getElementById("a2");
      const a3 = document.getElementById("a3");
      // chain play, skip if src missing
      function playIfReady(a) {{
        if (!a) return Promise.resolve();
        return new Promise((res) => {{
          a.onended = () => res();
          a.onerror = () => res();
          // try to play; some browsers block autoplay unless user gesture — Streamlit click triggers it
          a.play().then(() => {{}}).catch(()=>{{}});
        }});
      }}
      (async () => {{
        await playIfReady(a1);
        await playIfReady(a2);
        await playIfReady(a3);
      }})();
    </script>
    """
    # Render small height to ensure script runs
    components.html(html, height=10)

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("🎓 KPRIET Multilingual Campus Voice Assistant")
st.markdown("#### 🗣️ Ask for directions or choose a location below")

# Manual Button Selection with unique keys
cols = st.columns(2)
for i, loc in enumerate(location_map.keys()):
    if cols[i % 2].button(loc.capitalize(), key=f"btn_{i}_{loc}"):
        resp = location_map[loc]["response"]
        # Translate
        ta = translate_text(resp, "ta")
        hi = translate_text(resp, "hi")
        # Show
        st.success(f"**English:** {resp}")
        st.info(f"**தமிழ்:** {ta}")
        st.warning(f"**हिन्दी:** {hi}")
        # Generate TTS (may need network for gTTS)
        b64_en = tts_to_b64(resp, "en")
        b64_ta = tts_to_b64(ta, "ta")
        b64_hi = tts_to_b64(hi, "hi")
        # Replace missing TTS with silent short mp3 if needed
        if not b64_en:
            st.error("English TTS failed.")
            b64_en = ""
        if not b64_ta:
            st.warning("Tamil TTS failed.")
            b64_ta = ""
        if not b64_hi:
            st.warning("Hindi TTS failed.")
            b64_hi = ""
        # Play sequentially in browser
        play_three_in_browser(b64_en, b64_ta, b64_hi)

st.divider()

# Voice Input Section
if st.button("🎤 Voice Query", key="voice_query"):
    record_audio()
    model = load_whisper()
    user_text = ""
    try:
        # use model.transcribe on saved WAV file
        result = model.transcribe(AUDIO_FILE)
        user_text = result.get("text", "").lower().strip()
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        user_text = ""

    time.sleep(0.2)
    if user_text:
        st.write(f"📝 You said: `{user_text}`")
        resp = find_location_response(user_text)
        ta = translate_text(resp, "ta")
        hi = translate_text(resp, "hi")
        st.success(f"**English:** {resp}")
        st.info(f"**தமிழ்:** {ta}")
        st.warning(f"**हिन्दी:** {hi}")
        # TTS generation
        b64_en = tts_to_b64(resp, "en")
        b64_ta = tts_to_b64(ta, "ta")
        b64_hi = tts_to_b64(hi, "hi")
        play_three_in_browser(b64_en or "", b64_ta or "", b64_hi or "")
    else:
        st.warning("No valid voice input detected. Please try again.")

st.caption("Developed by Haresh | CSE (AI & ML) | KPRIET 🎓")
