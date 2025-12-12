# 🎤 Multilingual Voice Assistant

A powerful **AI Voice Assistant** capable of:

✅ Recording voice input
✅ Transcribing speech using **Whisper**
✅ Translating text into multiple languages
✅ Generating voice responses
✅ Running locally or inside a DevContainer
✅ Supporting multiple audio formats (`wav`, `mp3`)

This repository contains all scripts, audio samples, utilities, and configuration files required to run the assistant.

---

## 📂 Project Structure

```
.
├── .devcontainer/                # VS Code dev-container setup
├── MultilingualVoiceAssistant/   # Main Voice Assistant module
├── utils/                        # Helper utilities (audio processing, etc.)
│
├── MultilingualVoiceAssistant.zip # Compressed source (backup/export)
├── app.py                        # Main Streamlit / GUI App
├── voice_assistant.py            # Core assistant logic
├── whis.py                       # Whisper STT module
├── warn.py                       # Warning/notification system
├── test.py                       # Test script
├── input.wav                     # Sample input audio
├── logo.png                      # Project logo for UI
├── temp.mp3                      # Temporary audio output
├── ta_test.mp3                   # Test audio file
├── requirements.txt              # Dependencies
```

---

# 🚀 Features

### 🗣️ Speech-to-Text (STT)

* Uses **OpenAI Whisper** (local or API-based)
* Supports noisy audio
* Works with `.wav` and `.mp3`

### 🌍 Multilingual Translation

* Detects spoken language automatically
* Translates to any supported language (English, Tamil, Hindi, etc.)

### 🔊 Text-to-Speech (TTS)

* Converts the assistant's response into audio
* Plays back output instantly

### 🎛️ Streamlit Interface (Optional)

* Simple UI to upload audio
* View transcription and translation
* Play generated voice

### 🧪 Test Scripts Included

* Run sample audio files
* Validate Whisper installation
* Debug environment

---

# 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd <project-directory>
```

### 2️⃣ Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

If Whisper fails to install on Windows, run:

```bash
pip install git+https://github.com/openai/whisper.git 
```

---

# 🧠 Usage

## ▶️ Run the Assistant (CLI mode)

```bash
python voice_assistant.py
```

This will:

1. Record/Load audio
2. Transcribe using Whisper
3. Translate text
4. Generate voice output

---

## ▶️ Run the Streamlit App

```bash
streamlit run app.py
```

Features:

* Upload `.wav` or `.mp3`
* View transcription
* Play voice output
* Select translation language

---

# 🔧 Scripts Overview

### 📌 `app.py`

* Streamlit UI
* File upload
* Audio play
* Calls Whisper + TTS pipeline

### 📌 `voice_assistant.py`

* Core logic
* Microphone input
* Whisper inference
* Translation + TTS

### 📌 `whis.py`

* Encapsulates Whisper model
* STT utilities

### 📌 `warn.py`

* Custom warning and notification messages

### 📌 `test.py`

* Tests environment + verifies Whisper model

---

# 🔊 Example Command-Line Output

```
[Listening...]
→ Detected language: en  
→ Transcription: "Hello, how are you?"  
→ Translation (Tamil): "வணக்கம், எப்படி இருக்கிறீர்கள்?"  
→ Generating voice response...  
[Playing audio]
```

---

# 🧪 Testing the Environment

Run:

```bash
python test_env.py
```

Checks installed packages and Whisper availability.

---

# 🐳 Dev Container Support

The `.devcontainer/` folder lets you run the project in:

* GitHub Codespaces
* VS Code Dev Container

With automatic installation of:

* FFmpeg
* Whisper
* Torch
* TTS models

---

# 🤝 Contributing

Feel free to open:

* Issues
* Feature requests
* Pull requests

---

Would you like the **advanced README** version?
