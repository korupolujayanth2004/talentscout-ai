---
title: TalentScout AI
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.27.0"  
app_file: frontend/app.py
pinned: false
---

# TalentScout AI Hiring Assistant

An intelligent chatbot for technical candidate screening — built with Python, Streamlit, FastAPI, Groq/Llama, and Qdrant.

## 🚀 Features

- **Friendly Chat UI:** Modern, multi-step, streaming chat interface (Streamlit)
- **Resume PDF Parsing:** Extracts name, contact info, tech stack, and experience
- **LLM-Driven Interview:** Interactive, context-aware interview using Groq (Llama3-70B)
- **Auto-Generated Tech Questions:** Dynamic based on declared tech stack
- **Session-Based Memory:** Each candidate’s interview stored and managed separately
- **Professional Summaries:** AI-generated, downloadable assessments
- **Robust Data Handling:** Secure, session-based storage, easy clearing

## 🛠️ Tech Stack

- Python 3.10+
- [Streamlit](https://streamlit.io/) (chat UI)
- FastAPI (backend API)
- Groq/Llama3 (or OpenAI GPT API)
- Qdrant (vector DB for session state)
- PyMuPDF (resume PDF parsing)

## 🔧 Setup & Installation

1. **Clone repo:**  
   `git clone https://github.com/korupolujayanth2004/talentscout-ai.git`

2. **Environment:**  
   `python3 -m venv venv && source venv/bin/activate`

3. **Install requirements:**  
   `pip install -r requirements.txt`

4. **Run Backend API:**  
    `cd backend`  
    `uvicorn main:app --reload`

5. **Run Frontend/Chat:**  
    `cd frontend`  
    `streamlit run app.py`

## ❓ Usage

- Upload your resume or enter info manually
- Chat with the AI for a fully interactive “real interview” experience
- Download summary and feedback afterwards

## 🎯 Prompt Engineering Notes

- Information extraction prompt guides the LLM to only ask for missing fields
- Tech question prompt takes in tech stack, requests only conceptual/practical questions
- Summarizer prompt polishes the conversation history and returns a clear HR report

## 🏆 Performance and Extensions

- API responses are cached for common questions (performance)
- Can be extended with emotion/sentiment analysis and multilingual support

## 📄 License

MIT
