import os
import queue
import sounddevice as sd
import sys
import json
import numpy as np
import pyttsx3
import tempfile
import time
from vosk import Model, KaldiRecognizer
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.io.wavfile import write as write_wav

# --- Paths ---
MODEL_PATH = os.path.expanduser("model")
REFERENCE_EMBEDDING_PATH = "arma_embedding.npy"

# --- Globals ---
q = queue.Queue()
engine = pyttsx3.init()
encoder = VoiceEncoder()

# --- Load Model ---
print("Loading Vosk model...")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
print("Vosk model loaded!")

# --- TTS Helper ---
def speak(text):
    print(f"[Assistant]: {text}")
    engine.say(text)
    engine.runAndWait()

# --- Audio Callback ---
def callback(indata, frames, time, status):
    if status:
        print(f"[ERROR]: {status}", file=sys.stderr)
    q.put(bytes(indata))

# --- Recognize Speech Helper ---
def recognize_speech(timeout=8):
    """Listens from mic and returns recognized text"""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("🎤 Listening for speech...")
        rec = KaldiRecognizer(model, 16000)
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print("⏱️ Timeout reached")
                return None
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get("text"):
                    print(f"🗣️ Recognized: {result['text']}")
                    return result["text"]
        return None

# --- Phrase Listener ---
def listen_for_phrase(target_phrase="infinity", timeout=10):
    print("👂 Waiting for secret phrase...")
    while True:
        phrase = recognize_speech(timeout=timeout)
        if phrase is None:
            speak("Didn't hear anything, try again.")
            continue
        if target_phrase.lower() in phrase.lower():
            speak("Secret phrase recognized.")
            return True
        else:
            speak("Wrong phrase, try again.")

# --- Save temp WAV for voice identity ---
def record_voice_to_file(file_path="temp_voice.wav", duration=3):
    print(f"🎙️ Recording voice sample for {duration} seconds...")
    myrecording = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait()
    write_wav(file_path, 16000, myrecording)
    print(f"💾 Saved voice to {file_path}")

# --- Verify voice using embedding ---
def verify_secret_phrase_by_voice(threshold=0.6):
    reference_embedding = np.load(REFERENCE_EMBEDDING_PATH)
    temp_wav_path = "temp_voice.wav"
    record_voice_to_file(temp_wav_path, duration=3)

    try:
        wav = preprocess_wav(temp_wav_path)
        test_embedding = encoder.embed_utterance(wav)
        similarity = np.inner(reference_embedding, test_embedding)
        print(f"📊 Similarity Score: {similarity:.3f}")

        os.remove(temp_wav_path)
        if similarity >= threshold:
            return True
        else:
            return False
    except Exception as e:
        print(f"⚠️ Error verifying voice: {e}")
        return False

# --- Command Listener (optional) ---
def listen_for_command():
    speak("What do you want me to do?")
    command = recognize_speech(timeout=5)
    if command:
        if "mail" in command:
            speak("Opening your mail.")
            os.system("open mail")  # macOS only
        elif "lock" in command:
            speak("Locking your Mac.")
            os.system("pmset displaysleepnow")  # simulate screen lock
        else:
            speak("Command not recognized.")
    else:
        speak("No command heard.")

# Define keywords for intent recognition
INTENT_KEYWORDS = {
    "open_browser": ["open chrome", "open google chrome", "launch browser", "start chrome"],
    "open_mail": ["open mail", "check email", "launch mail"],
    "play_music": ["play music", "start music", "launch music"],
    "open_code": ["open code", "launch vs code", "start visual studio"],
    "shutdown": ["shut down", "shutdown", "turn off"],
    "default_unlock": ["unlock", "i'm back", "hello"]
}


# --- Main Flow ---
def main():
    speak("Mac voice lock system ready.")

    if listen_for_phrase(target_phrase="infinity"):
        if verify_secret_phrase_by_voice():
            speak("Voice verified. Welcome back, Arma.")
            # 👇 Add actual unlock logic or system command here
            # os.system("your_unlock_command")
            # For now, we'll just listen for a command
            listen_for_command()
        else:
            speak("Access denied. Voice mismatch.")

if __name__ == "__main__":
    main()

