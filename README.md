# 🚖 Ola Hindi Voice Support Bot

A real-time **voice-enabled Hindi support bot** for Ola drivers, built using:
- 🎙️ SpeechRecognition (speech → text)
- 🤖 OpenAI GPT (LLM brain)
- 🔊 gTTS + Pygame (text → speech)
- 🌐 Streamlit (UI)

---

## ⚡ Architecture

```mermaid
flowchart TD
    A[Driver Speech 🎤] --> B[SpeechRecognition STT]
    B --> C[LangDetect]
    C --> D[OpenAI GPT LLM 🤖]
    D --> E[gTTS TTS 🔊]
    E --> F[Pygame Audio Player]
    D --> G[Streamlit UI 🖥️]