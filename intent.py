import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Supported intents — expand this list if you want bonus points
INTENTS = ["create_file", "write_code", "summarize", "general_chat"]

SYSTEM_PROMPT = """
You are an intent classifier for a voice-controlled AI agent.

Given a user's transcribed speech, return a JSON object with:
- "intent": one of ["create_file", "write_code", "summarize", "general_chat"]
- "confidence": a float between 0 and 1
- "extracted_info": a short string with relevant details (filename, topic, language, etc.)

Rules:
- "create_file" → user wants to create an empty file or folder
- "write_code" → user wants code generated and saved to a file
- "summarize" → user wants text or a topic summarized
- "general_chat" → anything else (questions, conversation, greetings)

Respond ONLY with valid JSON. No explanation, no markdown.

Examples:
Input: "Create a file called notes.txt"
Output: {"intent": "create_file", "confidence": 0.98, "extracted_info": "filename: notes.txt"}

Input: "Write a Python function that sorts a list"
Output: {"intent": "write_code", "confidence": 0.97, "extracted_info": "language: Python, task: sort a list"}

Input: "Summarize what machine learning is"
Output: {"intent": "summarize", "confidence": 0.95, "extracted_info": "topic: machine learning"}

Input: "Hey what's the weather like?"
Output: {"intent": "general_chat", "confidence": 0.90, "extracted_info": "casual question about weather"}
"""


def detect_intent(transcribed_text: str) -> dict:
    """
    Sends transcribed text to Groq LLM and returns
    a dict with intent, confidence, and extracted_info.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcribed_text},
            ],
            temperature=0.1,  # low temp = consistent classification
            max_tokens=150,
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        # safety fallback if model returns unexpected keys
        return {
            "intent": result.get("intent", "general_chat"),
            "confidence": round(result.get("confidence", 0.5), 2),
            "extracted_info": result.get("extracted_info", ""),
        }

    except json.JSONDecodeError:
        return {
            "intent": "general_chat",
            "confidence": 0.0,
            "extracted_info": "Failed to parse intent — defaulting to chat",
        }
    except Exception as e:
        return {
            "intent": "general_chat",
            "confidence": 0.0,
            "extracted_info": f"Error: {str(e)}",
        }


if __name__ == "__main__":
    tests = [
        "Create a Python file with a retry function",
        "Summarize the concept of neural networks",
        "Make a folder called projects",
        "What time is it?",
    ]
    for t in tests:
        print(f"\nInput : {t}")
        print(f"Result: {detect_intent(t)}")