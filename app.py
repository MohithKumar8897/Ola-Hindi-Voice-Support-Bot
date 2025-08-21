# app.py
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
import time
from openai import OpenAI
from langdetect import detect
import os

# -------------------- CONFIG --------------------
openai_client = OpenAI(api_key="Api Key")
pygame.mixer.init()

# -------------------- VOICE FUNCTIONS --------------------
def speak(text):
    tts = gTTS(text=text, lang="hi")
    temp_file = tempfile.NamedTemporaryFile(delete=True)
    file_path = temp_file.name + ".mp3"
    tts.save(file_path)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def listen(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Kripya bolein...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=timeout)
            text = r.recognize_google(audio, language="hi-IN")
            st.success(f"🗣️ Aapne kaha: {text}")
            return text
        except sr.WaitTimeoutError:
            st.error("⚠️ Sunne mein timeout ho gaya.")
            return ""
        except sr.UnknownValueError:
            st.error("⚠️ Samajh nahi aaya. Kripya phir se bolein.")
            return ""
        except sr.RequestError:
            st.error("⚠️ Google Speech API error.")
            return ""

# -------------------- LLM FUNCTIONS --------------------
def get_bot_response(prompt):
    """Get bot response using new OpenAI v1 API"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful customer support agent for Ola drivers. Respond in Hindi."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ GPT API Error: {e}")
        return "Kripya thodi der mein phir se koshish karein."

def interpret_driver_response(text):
    prompt = f"Driver ne kaha: '{text}'. Kya iska matlab 'yes' hai ya 'no'? Sirf yes/no me reply karein."
    return get_bot_response(prompt).strip().lower()

def handle_unexpected_response(user_text):
    prompt = f"Driver ne unexpected baat kahi: '{user_text}'. Aap customer support agent hain. Kripya Hindi me short aur polite response dein."
    return get_bot_response(prompt)

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Ola Hindi Voice Bot", layout="centered")
st.title("🚖 Ola Hindi Voice Support Bot")
st.markdown("""
This is a **real-time Hindi voice bot** for Ola driver support.
Click **Start Call** and follow the prompts.
""")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("📞 Start Call"):
    driver_init = "Main 2 ghante se online hoon par mujhe koi ride nahi mil rahi."
    st.write(f"Driver: {driver_init}")
    speak(driver_init)
    st.session_state.chat_history.append({"user": driver_init, "bot": ""})

    bot_prompt = "Ola customer support mein aapka swagat hai. Kya yeh aapka registered number hai?"
    st.write(f"Bot: {bot_prompt}")
    speak(bot_prompt)
    st.session_state.chat_history.append({"user": "", "bot": bot_prompt})

    user_response = ""
    for i in range(3):
        user_response = listen()
        if user_response:
            try:
                lang = detect(user_response)
                if lang != "hi":
                    st.warning("⚠️ Kripya Hindi mein bolein.")
                    speak("Kripya Hindi mein bolein.")
                    continue
            except:
                pass
            break
    else:
        st.warning("⚠️ Microphone mein problem ya samajh nahi aaya. Call continue kar rahe hain.")

    st.session_state.chat_history.append({"user": user_response, "bot": ""})

    interpreted = interpret_driver_response(user_response)
    if interpreted == "yes":
        st.success("✅ Driver confirmed registered number.")
    elif interpreted == "no":
        st.warning("⚠️ Driver said the number is not registered.")
    else:
        bot_response = handle_unexpected_response(user_response)
        st.info(f"Bot: {bot_response}")
        speak(bot_response)
        st.session_state.chat_history.append({"user": "", "bot": bot_response})

    bot_response = "Aapka number blocked nahi hai. Sab theek hai."
    st.write(f"Bot: {bot_response}")
    speak(bot_response)
    st.session_state.chat_history.append({"user": "", "bot": bot_response})
    time.sleep(1)

    bot_response = "Kripya apna location badal kar phir se rides check kijiye."
    st.write(f"Bot: {bot_response}")
    speak(bot_response)
    st.session_state.chat_history.append({"user": "", "bot": bot_response})

    st.balloons()
    st.success("✅ Call ended. Shukriya!")
