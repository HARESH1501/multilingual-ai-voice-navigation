import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import pyttsx3
from deep_translator import GoogleTranslator
from gtts import gTTS
from playsound import playsound
import os
import time
from difflib import get_close_matches

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QMessageBox, QSizePolicy, QScrollArea, QFrame
)
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt, QThread, Signal

# Set ffmpeg path
os.environ["PATH"] += os.pathsep + r"C:\Users\Haresh\OneDrive\Desktop\New folder\ffmpeg-7.1.1-essentials_build (3)\ffmpeg-7.1.1-essentials_build\bin"

# --- Location data ---
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


# Create synonym mapping
synonym_to_key = {}
for key, val in location_map.items():
    for syn in val["synonyms"]:
        synonym_to_key[syn.lower()] = key

DURATION = 6
FS = 44100
AUDIO_FILE = "input.wav"

# Initialize TTS engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'en' in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break


def record_audio(filename=AUDIO_FILE, duration=DURATION, fs=FS):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, recording)


def speak_text_pyttsx3(text):
    engine.say(text)
    engine.runAndWait()


def speak_text_gtts(text, lang, filename):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    playsound(filename)
    os.remove(filename)


def translate_text(text, lang_code):
    """Fix: ensure translation happens into correct language"""
    translator = GoogleTranslator(source="auto", target=lang_code)
    return translator.translate(text)


def transcribe_audio(filename=AUDIO_FILE):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result["text"].lower()


def fuzzy_location_match(user_text):
    words = user_text.split()
    all_synonyms = list(synonym_to_key.keys())
    candidates = []
    for word in words:
        matches = get_close_matches(word, all_synonyms, n=1, cutoff=0.7)
        if matches:
            candidates.append(matches[0])
    if candidates:
        return synonym_to_key[candidates[0]]
    return None


def find_location_response(transcribed_text):
    for syn in synonym_to_key:
        if syn in transcribed_text:
            key = synonym_to_key[syn]
            return location_map[key]["response"]
    fuzzy_key = fuzzy_location_match(transcribed_text)
    if fuzzy_key:
        return location_map[fuzzy_key]["response"]
    return "Sorry, I don't have information about that location yet."


def show_message_box(title, message):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #1E1E1E;
            color: black;
            font-size: 14px;
        }
        QPushButton {
            background-color: #0078D7;
            color: white;
            padding: 5px;
            border-radius: 5px;
            min-width: 60px;
        }
    """)
    msg.exec()


# --- Voice query worker ---
class VoiceWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def run(self):
        try:
            record_audio()
            text = transcribe_audio()
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


# --- Main GUI ---
class CampusAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎓 KPRIET Campus Voice Assistant - Advanced")
        self.setGeometry(100, 100, 500, 600)

        # Background
        background = QPixmap(r"C:\Users\Haresh\OneDrive\Desktop\project 1\logo.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background.scaled(self.size(), Qt.KeepAspectRatioByExpanding)))
        self.setPalette(palette)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll.setWidget(scroll_content)
        self.scroll_layout = QVBoxLayout(scroll_content)

        self.label = QLabel("Select a location or use Voice Query")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #003366; background-color: rgba(255, 255, 255, 180); padding: 8px;")
        self.label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.label)

        self.btn_voice = QPushButton("🎙️ Voice Query")
        self.btn_voice.setStyleSheet("font-size: 16px; background-color: white; border: 2px solid #003366; color: #003366; padding: 6px;")
        self.btn_voice.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_voice.clicked.connect(self.voice_query_clicked)
        self.scroll_layout.addWidget(self.btn_voice)

        # Dynamic location buttons
        self.locations = list(location_map.keys())
        for loc in self.locations:
            btn = QPushButton(loc.capitalize())
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    background-color: white;
                    color: #003366;
                    border: 1px solid #003366;
                    padding: 5px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, l=loc: self.location_clicked(l))
            self.scroll_layout.addWidget(btn)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: #003366; margin-top: 10px; background-color: rgba(255, 255, 255, 180); padding: 4px;")
        self.scroll_layout.addWidget(self.status_label)

        self.btn_exit = QPushButton("❌ Exit")
        self.btn_exit.setStyleSheet("font-size: 14px; background-color: #FF4C4C; color: white; padding: 6px;")
        self.btn_exit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_exit.clicked.connect(self.close)
        self.scroll_layout.addWidget(self.btn_exit)

        self.kpr_text = QLabel("KPRIET Campus Navigation")
        self.kpr_text.setAlignment(Qt.AlignCenter)
        self.kpr_text.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background-color: rgba(0,0,0,70); padding: 10px;")
        self.scroll_layout.addWidget(self.kpr_text)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def set_status(self, message):
        self.status_label.setText(message)
        QApplication.processEvents()

    # Voice query
    def voice_query_clicked(self):
        self.set_status("🎤 Listening...")
        self.voice_worker = VoiceWorker()
        self.voice_worker.finished.connect(self.voice_query_finished)
        self.voice_worker.error.connect(self.voice_query_error)
        self.voice_worker.start()

    def voice_query_finished(self, user_text):
        self.set_status(f"📝 You said: {user_text}")
        response = find_location_response(user_text)
        self.set_status("🔊 Speaking response...")

        # ✅ Translate properly
        tamil_resp = translate_text(response, 'ta')
        hindi_resp = translate_text(response, 'hi')

        # Show multilingual message
        full_message = f"English: {response}\n\nதமிழ்: {tamil_resp}\n\nहिन्दी: {hindi_resp}"
        show_message_box("Campus Info", full_message)

        # Speak all three
        speak_text_pyttsx3(response)
        speak_text_gtts(tamil_resp, 'ta', "ta.mp3")
        speak_text_gtts(hindi_resp, 'hi', "hi.mp3")

        self.set_status("✅ Done.")

    def voice_query_error(self, err_msg):
        show_message_box("Error", f"Oops! Something went wrong.\n{err_msg}")
        self.set_status("Error occurred.")

    # Location button click
    def location_clicked(self, location_key):
        try:
            response = location_map[location_key]["response"]
            tamil_resp = translate_text(response, 'ta')
            hindi_resp = translate_text(response, 'hi')

            full_message = f"English: {response}\n\nதமிழ்: {tamil_resp}\n\nहिन्दी: {hindi_resp}"
            show_message_box("Campus Info", full_message)

            speak_text_pyttsx3(response)
            speak_text_gtts(tamil_resp, 'ta', "ta.mp3")
            speak_text_gtts(hindi_resp, 'hi', "hi.mp3")

        except Exception as e:
            show_message_box("Error", f"Oops! Something went wrong.\n{str(e)}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CampusAssistant()
    window.show()
    sys.exit(app.exec())
