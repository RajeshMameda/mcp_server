from dotenv import load_dotenv
import os
from openai import OpenAI
from PyPDF2 import PdfReader
import gradio as gr

load_dotenv(override=True)

openai=OpenAI()

reader = PdfReader("Profile.pdf")

Linkedin = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        Linkedin += text

with open("profile.txt", "r", encoding="utf-8") as f:
    summary = f.read()

name = "Rajesh Mameda"

system_prompt = f" you are acting as {name}.you are answering the questions on {name}'s website. \
    particularly questions related to {name}'s carrer, backgroung, skills and experience. \
    your responsiblity is to represent {name} for interaction on the website as faithufully as possbile. \
    your given a summary of {name}'s backgorund and Linkden profile which you can use to answer questions. \
    be professional and engaging, as if talking to a potentional client or future employer who came across the website if you dont'know the answer, say so."
    
system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile\n{Linkedin}\n\n"
system_prompt += f"with this content, please chat with the user, always staying in character as {name}."

def chat(message, history):
    messages = [{"role":"system", "content": system_prompt}] + history + [{"role":"user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

gr.ChatInterface(chat, type="messages").launch()

