import pyttsx3

# Note this is useful to catch errors in your writing. There are more powerful models for this available in HuggingFace.
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
