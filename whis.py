import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import pyttsx3
from googletrans import Translator
from gtts import gTTS
from playsound import playsound
import os
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Set ffmpeg path
os.environ["PATH"] += os.pathsep + r"C:\\Users\\Haresh\\OneDrive\\Desktop\\New folder\\ffmpeg-7.1.1-essentials_build (3)\\ffmpeg-7.1.1-essentials_build\\bin"

# 📌 Location response mapping
location_map = {
    "library": "The central library is located in the S&H block.",
    "admin": "The admin block is next to the main entrance.",
    "canteen": "The canteen is behind Block C near the sports ground.",
    "lab": "The AI-ML lab is in Block B, 3rd floor.",
    "parking": "Go straight from the E Gate."
}

# 🎙️ Record audio
def record_audio(filename="input.wav", duration=5, fs=44100):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, recording)

# 🔊 Speak in English (offline)
def speak_text_pyttsx3(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'en' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()

# 🗣️ Speak in Tamil & Hindi
def speak_text_gtts(text, lang, filename):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# 🌐 Translate text
def translate_text(text, lang_code):
    translator = Translator()
    translated = translator.translate(text, dest=lang_code)
    return translated.text

# 🧠 Transcribe voice to text
def transcribe_audio(filename="input.wav"):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result["text"].lower()

# 🗺️ Find campus location info
def find_location_response(transcribed_text):
    for key in location_map:
        if key in transcribed_text:
            return location_map[key]
    return "Sorry, I don't have information about that location yet."

# 🧠 Combined logic
def handle_voice_query():
    record_audio()
    user_text = transcribe_audio()
    response = find_location_response(user_text)
    show_and_speak(response)

# 💬 Show and speak the response
def show_and_speak(response):
    tamil_resp = translate_text(response, 'ta')
    hindi_resp = translate_text(response, 'hi')

    messagebox.showinfo("Campus Info", f"\nEnglish: {response}\n\nTamil: {tamil_resp}\n\nHindi: {hindi_resp}")

    speak_text_pyttsx3(response)
    speak_text_gtts(tamil_resp, 'ta', "ta.mp3")
    speak_text_gtts(hindi_resp, 'hi', "hi.mp3")
    root.quit()

# 🔘 Handle button clicks
def handle_button_click(location):
    response = location_map.get(location, "No data available.")
    show_and_speak(response)

# 🎨 Advanced GUI setup
root = tk.Tk()
root.title("🎓 KPRIET Campus Voice Assistant")
root.geometry("600x600")
root.configure(bg="#eef7fa")

frame = tk.Frame(root, bg="#eef7fa")
frame.pack(pady=20)

label = tk.Label(frame, text="Select a location or use Voice Query", font=("Arial", 14, "bold"), bg="#eef7fa")
label.pack(pady=10)

btn_voice = tk.Button(frame, text="🎙️ Voice Query", font=("Arial", 12), width=25, command=handle_voice_query, bg="#ffffff")
btn_voice.pack(pady=8)

locations = ["library", "admin", "canteen", "lab", "parking"]
for loc in locations:
    tk.Button(frame, text=loc.capitalize(), font=("Arial", 11), width=25, command=lambda l=loc: handle_button_click(l), bg="#d1f0d7").pack(pady=5)

# 🗺️ Campus map view
try:
    map_img = Image.open("campus_map.jpg")  # Replace with your actual image
    map_img = map_img.resize((400, 250))
    map_photo = ImageTk.PhotoImage(map_img)
    map_label = tk.Label(root, image=map_photo, bg="#eef7fa")
    map_label.image = map_photo
    map_label.pack(pady=10)
except Exception as e:
    error_label = tk.Label(root, text="Campus map not found.", bg="#eef7fa", fg="red")
    error_label.pack(pady=10)

exit_btn = tk.Button(root, text="❌ Exit", font=("Arial", 11), width=15, command=root.quit, bg="#f8d7da")
exit_btn.pack(pady=10)

root.mainloop()
