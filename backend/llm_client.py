import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
model_name = "llama3-70b-8192"  # example model

def generate_technical_questions(tech_stack):
    prompt = (
        "You are an expert technical interviewer. Create 3-5 concise and relevant technical "
        "questions to assess a candidate's proficiency in the following technologies: "
        + ", ".join(tech_stack) +
        ". Include conceptual, practical, and problem-solving questions."
    )
    messages = [
        {"role": "system", "content": "You are a helpful, expert interviewer."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=False
    )
    content = response.choices[0].message.content.strip()
    questions = [q.strip() for q in content.split("\n") if q.strip()]
    return questions[:5]

def chat_with_llm(messages):
    """Handle chat conversation with LLM"""
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=False
    )
    return response.choices[0].message.content.strip()
