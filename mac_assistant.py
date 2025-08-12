import pyttsx3
import subprocess
import sys

from voice_auth import listen_for_phrase, recognize_speech, INTENT_KEYWORDS

engine = pyttsx3.init()

def speak(text):
    print("Arma Sahar:", text)
    engine.say(text)
    engine.runAndWait()

def open_mac_app(app_name):
    try:
        subprocess.run(["open", "-a", app_name], check=True)
    except subprocess.CalledProcessError:
        speak(f"Sorry, couldn't open {app_name}.")

def handle_intent(intent_name):
    if intent_name == "open_mail":
        speak("Opening your email, boss!")
        open_mac_app("Mail")

    elif intent_name == "play_music":
        speak("Playing your favorite music.")
        open_mac_app("Music")

    elif intent_name == "open_code":
        speak("Launching Visual Studio Code.")
        open_mac_app("Visual Studio Code")

    elif intent_name == "open_chrome":
        speak("Opening Google Chrome.")
        open_mac_app("Google Chrome")

    elif intent_name == "shutdown":
        speak("Shutting down the system. Farewell!")
        subprocess.run(['osascript', '-e', 'tell app "System Events" to shut down'])

    elif intent_name == "default_unlock":
        speak("Unlocked! Awaiting your next command.")

    else:
        speak("Sorry Boss, I didn’t understand what you meant.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    speak("Listening for your secret command Arma...")

    intent = listen_for_phrase()

    if intent == "authentication_success":
        speak("Hey Arma, welcome back boss!")

        recognized_text = recognize_speech()
        print(f"Recognized command: '{recognized_text}'")

        normalized_text = recognized_text.lower().strip()
        detected_intent = "default_unlock"

        for intent_name, keywords_list in INTENT_KEYWORDS.items():
            for keyword in keywords_list:
                if keyword in normalized_text:
                    detected_intent = intent_name
                    break
            if detected_intent != "default_unlock":
                break

        print(f"🧠 Detected intent: {detected_intent}")
        handle_intent(detected_intent)

    else:
        speak("Access denied. You're not the boss!")
        sys.exit(1)

