import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import requests
import speech_recognition as sr
import pyttsx3
import os
import socket
from llama_cpp import Llama

# ================= CONFIG =================
OPENROUTER_API_KEY = "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"
MODEL = "mistralai/mistral-7b-instruct"

# ================= LOAD OFFLINE MODEL =================
llm = Llama(
    model_path=r"C:\Users\Varshini\Desktop\jarvis\New folder\mistral-7b-instruct-v0.1.Q5_K_S.gguf",
    n_ctx=32768,
    n_threads=20,
    n_batch=256
)

# ================= VOICE =================
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak_async(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

# ================= INTERNET CHECK =================
def is_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# ================= ONLINE AI =================
def ask_online(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=5
        )

        if r.status_code != 200:
            return None

        return r.json()["choices"][0]["message"]["content"]

    except:
        return None

# ================= OFFLINE AI =================
def ask_offline(prompt):
    try:
        output = llm(
            f"[INST] You are JARVIS, a smart AI assistant.\nUser: {prompt} [/INST]",
            max_tokens=200,
            temperature=0.7,
            stop=["</s>"]
        )
        return output["choices"][0]["text"].strip()

    except Exception as e:
        return f"⚠ Offline error: {str(e)}"

# ================= HYBRID AI =================
def ask_ai(prompt):
    if is_internet():
        reply = ask_online(prompt)
        if reply:
            return "🌐 " + reply

    return "💻 " + ask_offline(prompt)

# ================= PROCESS INPUT =================
def process_input(text):
    if not text.strip():
        return

    chat_area.insert(tk.END, f"You: {text}\n", "user")
    chat_area.insert(tk.END, "Jarvis: Thinking...\n", "ai")
    entry.delete(0, tk.END)

    def run():
        reply = ask_ai(text)

        def update_ui():
            chat_area.delete("end-2l", "end-1l")
            chat_area.insert(tk.END, f"Jarvis: {reply}\n", "ai")

        root.after(0, update_ui)
        speak_async(reply)

    threading.Thread(target=run, daemon=True).start()

# ================= AUTO VOICE =================
def auto_listen():
    rec = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        try:
            with mic as source:
                audio = rec.listen(source, phrase_time_limit=5)

            text = rec.recognize_google(audio)

            def update_ui():
                chat_area.insert(tk.END, f"You (Voice): {text}\n", "user")

            root.after(0, update_ui)
            process_input(text)

        except:
            pass

# ================= UI =================
root = tk.Tk()
root.title("JARVIS HYBRID AI")
root.geometry("800x600")
root.configure(bg="#0a0a0a")

glass = tk.Frame(root, bg="#111111", bd=0)
glass.place(relx=0.5, rely=0.5, anchor="center", width=750, height=500)

chat_area = ScrolledText(
    glass,
    bg="#000000",
    fg="lime",
    font=("Consolas", 12),
    bd=0,
    insertbackground="white"
)
chat_area.pack(fill="both", expand=True, padx=10, pady=10)

chat_area.tag_config("user", foreground="#00ffcc")
chat_area.tag_config("ai", foreground="#00ffff")

entry = tk.Entry(
    root,
    font=("Consolas", 12),
    bg="#111111",
    fg="cyan",
    insertbackground="white",
    bd=0
)
entry.place(relx=0.5, rely=0.93, anchor="center", width=500)

entry.bind("<Return>", lambda e: process_input(entry.get()))

btn = tk.Button(
    root,
    text="🎤",
    command=lambda: threading.Thread(target=auto_listen, daemon=True).start(),
    bg="#111111",
    fg="cyan",
    bd=0
)
btn.place(relx=0.85, rely=0.93)

# Start voice once
threading.Thread(target=auto_listen, daemon=True).start()

speak_async("Welcome back, Santa")

root.mainloop()
