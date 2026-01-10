import json
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import model_client
from model_client import ModelClientError

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = "fixed-chat-2024"

chat_history = []

@app.route("/")
def chat():
    return render_template("chat_fixed.html", chat_history=chat_history)

@app.route("/send", methods=["POST"])
def send_message():
    user_message = request.form.get("message", "").strip()
    if not user_message:
        flash("Please enter a message.", "error")
        return redirect(url_for("chat"))
    
    chat_history.append({"role": "user", "content": user_message})
    
    try:
        # Use the SAME AI that generated your artifacts
        system_prompt = """You are an expert project planning assistant. Provide specific, actionable advice for the user's actual project."""
        
        # Build context from their real project
        context = ""
        control_file = BASE_DIR / "control.md"
        if control_file.exists():
            context = f"\nProject Context:\n{control_file.read_text(encoding='utf-8')[:1500]}"
        
        user_prompt = f"User question: {user_message}\n{context}\n\nProvide specific, actionable advice:"
        
        # Force use of working model - same one that generated your artifacts
        ai_response = model_client.generate_text(
            system_prompt, 
            user_prompt, 
            model="llama3"  # Force use of the model that worked
        )
        
        chat_history.append({"role": "assistant", "content": ai_response})
        flash("✅ AI response generated successfully!", "success")
        
    except Exception as e:
        error_msg = f"❌ AI Error: {str(e)}\n\nTry: 1) Ensure Ollama is running 2) Run 'ollama pull llama3' 3) Check model_config.json"
        chat_history.append({"role": "assistant", "content": error_msg})
        flash("AI service unavailable - check Ollama setup", "error")
    
    return redirect(url_for("chat"))

@app.route("/clear", methods=["POST"])
def clear_chat():
    global chat_history
    chat_history = []
    flash("Chat cleared.", "success")
    return redirect(url_for("chat"))

if __name__ == "__main__":
    print("🚀 Starting Fixed AI Chat on http://127.0.0.1:5001")
    print("   Using REAL AI responses (no templates)")
    app.run(debug=True, port=5001)