import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ["PATH"] += os.pathsep + r"C:\Users\Haresh\OneDrive\Desktop\New folder\ffmpeg-7.1.1-essentials_build (3)\ffmpeg-7.1.1-essentials_build\bin"
import whisper

model = whisper.load_model("base")
result = model.transcribe("input.wav")
print(result["text"])
