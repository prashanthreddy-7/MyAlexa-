# alexa_clone.py
# Simple voice assistant using speech_recognition, pyttsx3, pywhatkit, wikipedia, pyjokes.
# Features: wake word "alexa", play song on YouTube, tell time, simple Wikipedia summary,
# respond to date/single/joke queries, and a fallback message.

import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import sys
import traceback

# --- Text-to-speech engine setup ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# set second voice if available, else default
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
# optional: adjust speaking rate
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 10)


def talk(text: str):
    """Speak the provided text and also print it for debugging."""
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


# --- Speech recognition setup ---
listener = sr.Recognizer()


def take_command(timeout=5, phrase_time_limit=7) -> str:
    """
    Listen from the microphone and return a lowercased command string.
    Returns empty string on failure.
    """
    command = ""
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = listener.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        # use Google's free recognizer (requires internet)
        command = listener.recognize_google(audio)
        command = command.lower()
        print("Heard:", command)
    except sr.WaitTimeoutError:
        print("No speech: timeout while waiting for phrase.")
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception:
        print("Unexpected error during listening:")
        traceback.print_exc()
    return command


def run_alexa():
    """
    Get command and handle actions:
      - 'play <song>' -> open YouTube and play
      - 'time' -> speak current time
      - 'who is <person>' or variations -> speak 1-sentence wiki summary
      - 'date' -> humorous refusal
      - 'are you single' -> humorous reply
      - 'joke' -> tell a joke
    """
    command = take_command()
    if not command:
        return  # nothing to do this loop

    # Wake-word handling: require "alexa" before acting (optional)
    if "alexa" in command:
        # remove the wake word
        command = command.replace("alexa", "").strip()
        print("Command after wake-word:", command)
    else:
        # If you prefer to require wake-word, return here:
        # return
        # or continue to accept commands without wake-word -- we'll accept both
        pass

    try:
        if command.startswith("play "):
            song = command.replace("play", "", 1).strip()
            if song:
                talk(f"Playing {song} on YouTube")
                pywhatkit.playonyt(song)
            else:
                talk("Please tell me the song name to play.")
        elif "time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            talk(f"Current time is {now}")
        elif command.startswith("who is ") or command.startswith("who the heck is ") or command.startswith("who's "):
            # handle different phrasings
            person = command.replace("who is", "").replace("who the heck is", "").replace("who's", "").strip()
            if not person:
                talk("Who do you want me to search for?")
            else:
                talk(f"Searching Wikipedia for {person}")
                try:
                    info = wikipedia.summary(person, sentences=1)  # short summary
                    talk(info)
                except wikipedia.DisambiguationError as e:
                    # many possible pages
                    talk(f"That name is ambiguous. For example: {e.options[0:5]}")
                except wikipedia.PageError:
                    talk("I couldn't find that person on Wikipedia.")
                except Exception:
                    talk("Sorry, I couldn't get information from Wikipedia right now.")
        elif "date" in command:
            talk("Sorry, I have a headache.")
        elif "are you single" in command:
            talk("I am in a relationship with Wi-Fi.")
        elif "joke" in command or "tell me a joke" in command:
            joke = pyjokes.get_joke()
            talk(joke)
        else:
            talk("Please say the command again.")
    except Exception:
        talk("I ran into an error while handling that command.")
        traceback.print_exc()


if __name__ == "__main__":
    talk("Hey! I am ready. Say 'Alexa' followed by a command.")
    try:
        while True:
            run_alexa()
    except KeyboardInterrupt:
        talk("Goodbye.")
        sys.exit(0)
