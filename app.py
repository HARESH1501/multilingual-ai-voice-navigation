# app.py
import streamlit as st
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile, os, time
from difflib import get_close_matches
import numpy as np
import base64
import streamlit.components.v1 as components
from scipy.io.wavfile import write 
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
    "admin": {
        "synonyms": ["admin", "admission office", "main block", "admin block", "administrative block"],
        "response": "Enter through the Security Gate and walk straight along the main road.Take the second left — this road leads to the Administrative Block."
    },
    "imperial hall": {
        "synonyms": ["imperial hall"],
        "response": "Enter through the Security Gate and walk straight along the main road.Take the second left — this road leads to the Administrative Block. The building will be on your right side, from there you can also find Imperial hall."
    },
    "exam cell": {
        "synonyms": ["coe", "exam cell", "coe & exam cell"],
        "response": "Enter through the Security Gate and walk straight. Take the second left to reach the Administrative Block. Then walk straight to the Main Block. The COE & Exam Cell is on the right side of the Main Block, near the staff rooms."
    },
    "mechanical": {
        "synonyms": ["mechanical", "mechanical block"],
        "response": "Walk in through the Security Gate. Take the second left — you’ll see the Admin Block on your right. Keep walking straight, pass the Main Block. Then take a right turn. You’ll reach the Mechanical Block at the end of the road."
    },
    "civil": {
        "synonyms": ["civil", "civil block"],
        "response": "From the Mechanical Block, walk straight and turn left. The Civil Block is the next building on your right."
    },
    "eee": {
        "synonyms": ["eee", "eee block"],
        "response": "From the Main Block, walk around the left side of the building. Continue straight. The EEE Block is the second building on the right, after the T&P Cell."
    },
    "s&h": {
        "synonyms": ["s&h", "science block", "sh block", "s and h block"],
        "response": "Enter through the Security Gate and walk straight. Keep walking on the main road. take the small right road near the Girls washroom. Keep walk on the road, the S&H Block is on the right side, just a few steps after the Library."
    },
    "food court": {
        "synonyms": ["food court"],
        "response": "Enter through the Security Gate and walk straight. Just after the parking area, you will see the Food Court on your left."
    },
    "bike parking": {
        "synonyms": ["bike parking"],
        "response": "Enter through the Security Gate and walk straight. You will see the Bike Parking area."
    },
    "car parking": {
        "synonyms": ["car parking"],
        "response": "Enter through the Security Gate and walk straight. Take the second left. You will see the Car Parking area on your left side, just before reaching the Administrative Block."
    },
    "dining": {
        "synonyms": ["dining", "dining hall"],
        "response": "Enter through the Security Gate and walk straight. The Dining Hall is on your left side, just behind the Student Bike Parking."
    },
    "just print": {
        "synonyms": ["just print", "stationery"],
        "response": "Enter through the Security Gate and take the first left. Keep walking on that road — you’ll see the JustPrint stationery shop right in front of you."
    },
    "bme": {
        "synonyms": ["bme block", "bme"],
        "response": "Enter through the Security Gate and take the first left. Then take a right turn and walk straight. After you pass Kalai Arangam on your left, you will see the BME Block directly in front of you."
    },
    "ece": {
        "synonyms": ["ece block", "ece"],
        "response": "Enter through the Security Gate and take the first left. Then take a right turn and walk straight. After passing Kalai Arangam, the ECE Block will be on your right side, just before reaching the BME Block."
    },
    "chemical": {
        "synonyms": ["chemical block", "chemical engineering"],
        "response": "Enter through the Security Gate and take the first left. Then turn right and walk straight. After you pass Kalai Arangam, the Chemical Engineering Block will be on your left side, opposite the ECE Block."
    },
    "cse": {
        "synonyms": ["cse block", "cse"],
        "response": "Enter through the Security Gate and walk straight. You’ll see the Imperial Hall on your right. Walk past the Imperial Hall — you’ll find a pathway beside it. Take that pathway — it will lead you to the Main Block. Walk straight past the Main Block. Continue straight until you see the pond. Cross the pond area and keep walking. Pass the Open-Air Theatre, then take a left turn. The CSE Block will be on your right side."
    },
    "open-air theatre": {
        "synonyms": ["open air theatre", "oat"],
        "response": "Enter through the Security Gate and walk straight. You will see the Imperial Hall on your right. Walk beside the Imperial Hall and take the pathway to reach the Main Block. Continue straight, walk past the pond. The Open-Air Theatre will be on your right, just before the CSE Block turn."
    },
    "boys toilet": {
        "synonyms": ["boys toilet", "gents restroom", "gents toilet"],
        "response": "Enter through the Security Gate and take the first left. Then take a right turn and walk straight. You’ll pass Kalai Arangam on your left. Just after that, you’ll reach the Chemical Engineering Block on your left. The Gents Toilet is located inside the Chemical Block, on the ground floor."
    },
    "girls toilet": {
        "synonyms": ["girls toilet", "ladies toilet", "girls restroom"],
        "response": "Enter through the Security Gate and take the first left. Then take a right turn and walk straight. You’ll pass Kalai Arangam on your left. Just after that, you’ll reach the Chemical Engineering Block on your left. The Ladies Toilet is located inside the Chemical Block, on the ground floor, just after the Boys Restroom"
    },
    "boys hostel": {
        "synonyms": ["boys hostel"],
        "response": "Enter through the Security Gate and walk straight. Take the first left, then turn right and continue walking. Go past Kalai Arangam — you’ll see the Boys Hostel on your left"
    },
    "girls hostel": {
        "synonyms": ["girls hostel"],
        "response": "Enter through the Security Gate and walk straight. Take a right near the roundana (circle) and walk straight on that road. Then take another right and continue walking. Take a left and walk a few steps — you’ll see the Girls Hostel on your left side."
    },
    "library": {
        "synonyms": ["library", "central library"],
        "response": "Enter through the Security Gate and walk straight. Keep walking on the main road. take the small right road near the Girls washroom. Keep walk on the road, you'll see library on your right."
    },
    "ragam hall": {
        "synonyms": ["ragam hall"],
        "response": "Enter through the Security Gate and walk straight. Keep walking on the main road. take the small right road near the Girls washroom. Keep walk on the road,take right .you'll see ragam hall near library."
    },
    "veena hall": {
        "synonyms": ["veena hall"],
        "response": "Enter through the Security Gate and walk straight. Keep walking on the main road. take the small right road near the Girls washroom. Keep walk on the road, take left. walk few steps, you'll see veena hall on your left."
    },
    "pallavi hall": {
        "synonyms": ["pallavi hall"],
        "response": "Enter through the Security Gate and walk straight. Keep walking on the main road. take the small right road near the Girls washroom. Keep walk on the road, take left. walk few steps, you'll see pallavi hall on your left."
    },
    "dhanam hall": {
        "synonyms": ["dhanam hall"],
        "response": "Walk in through the Security Gate. Take the second left — you’ll see the Admin Block on your right. Keep walking straight, pass the Main Block. Then take a right turn. You’ll reach the Mechanical Block at the end of the road. Go to the second floor — Thanam Hall will be on your right."
    },
    "ad block": {
        "synonyms": ["ad block"],
        "response": "Enter through the Security Gate and walk straight. Take the second left — you’ll see the Administrative Block on your right. Enter the Admin Block and go to the second floor. The AD Classrooms are located on the second floor of the Admin Block."
    },
    "sa office": {
        "synonyms": ["sa office"],
        "response": "Enter through the Security Gate and walk straight. Take the second left — you’ll see the Administrative Block on your right. Enter the Admin Block and go to the first floor. The SA Office is located on the first floor of the Admin Block."
    },
    "stone bench": {
        "synonyms": ["stone bench"],
        "response": "Enter through the Security Gate and walk straight. Keep walking on the main road and take the small right near the Boys Washroom. Continue on that road — you’ll see the stone bench area on your left side."
    },
    "rk": {
        "synonyms": ["rk"],
        "response": "Enter through the Security Gate and walk straight. Keep walking on the main road and take a left turn opposite the Boys Washroom. You’ll see RK on your right side."
    }
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
def record_audio():
    uploaded_file = st.file_uploader("🎤 Upload or record your voice", type=["wav", "mp3"])

    if uploaded_file is not None:
        with open(AUDIO_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ Audio uploaded successfully!")
        return True
    else:
        st.warning("Please upload a voice recording.")
        return False

# ----------------------------
# Whisper model load (fixed)
# ----------------------------
@st.cache_resource
def load_whisper():
    return WhisperModel("base", device="cpu")

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
        gTTS(text=text, lang=lang).save(fname)
        with open(fname, "rb") as f:
            b = f.read()
        b64 = base64.b64encode(b).decode("utf-8")
        try:
            os.remove(fname)
        except:
            pass
        return b64
    except Exception:
        return None

# ----------------------------
# Play three audios sequentially in browser using data URIs
# ----------------------------
def play_three_in_browser(b64_en, b64_ta, b64_hi):
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
      function playIfReady(a) {{
        if (!a) return Promise.resolve();
        return new Promise((res) => {{
          a.onended = () => res();
          a.onerror = () => res();
          a.play().catch(()=>{{}});
        }});
      }}
      (async () => {{
        await playIfReady(a1);
        await playIfReady(a2);
        await playIfReady(a3);
      }})();
    </script>
    """
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
        ta = translate_text(resp, "ta")
        hi = translate_text(resp, "hi")
        st.success(f"**English:** {resp}")
        st.info(f"**தமிழ்:** {ta}")
        st.warning(f"**हिन्दी:** {hi}")
        b64_en = tts_to_b64(resp, "en")
        b64_ta = tts_to_b64(ta, "ta")
        b64_hi = tts_to_b64(hi, "hi")
        play_three_in_browser(b64_en or "", b64_ta or "", b64_hi or "")

st.divider()

# Voice Input Section
if st.button("🎤 Voice Query", key="voice_query"):
    record_audio()
    model = load_whisper()

    user_text = ""
    try:
        segments, info = model.transcribe(AUDIO_FILE)
        user_text = "".join([seg.text for seg in segments]).lower().strip()
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

        b64_en = tts_to_b64(resp, "en")
        b64_ta = tts_to_b64(ta, "ta")
        b64_hi = tts_to_b64(hi, "hi")
        play_three_in_browser(b64_en or "", b64_ta or "", b64_hi or "")

    else:
        st.warning("No valid voice input detected. Please try again.")

st.caption("Developed by Haresh | CSE (AI & ML) | KPRIET 🎓")
