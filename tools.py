import os
import re
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# All generated files go here — never outside this folder
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _safe_path(filename: str) -> str:
    """Ensures all file operations stay inside the output/ folder."""
    basename = os.path.basename(filename)  # strips any path traversal attempts
    return os.path.join(OUTPUT_DIR, basename)


def create_file(extracted_info: str) -> dict:
    """
    Creates an empty file or folder based on extracted intent info.
    Returns a result dict with status, filename, and message.
    """
    filename = _parse_filename(extracted_info) or f"new_file_{_timestamp()}.txt"
    filepath = _safe_path(filename)

    try:
        if "folder" in extracted_info.lower() or "directory" in extracted_info.lower():
            os.makedirs(filepath, exist_ok=True)
            return {
                "status": "success",
                "filename": filepath,
                "message": f"Folder '{filepath}' created successfully.",
                "content": None,
            }
        else:
            with open(filepath, "w") as f:
                f.write("")
            return {
                "status": "success",
                "filename": filepath,
                "message": f"File '{filepath}' created successfully.",
                "content": "",
            }
    except Exception as e:
        return {"status": "error", "filename": None, "message": str(e), "content": None}


def write_code(transcribed_text: str, extracted_info: str) -> dict:
    """
    Generates code using Groq LLM and saves it to a file.
    """
    language = _parse_language(extracted_info) or "python"
    extension = _language_to_extension(language)
    filename = _parse_filename(extracted_info) or f"generated_{_timestamp()}{extension}"
    filepath = _safe_path(filename)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an expert {language} developer. "
                        "Write clean, well-commented code based on the user's request. "
                        "Return ONLY the code — no markdown fences, no explanation."
                    ),
                },
                {"role": "user", "content": transcribed_text},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        code = response.choices[0].message.content.strip()
        # strip accidental markdown code fences if model adds them
        code = re.sub(r"^```[\w]*\n?", "", code)
        code = re.sub(r"\n?```$", "", code)

        with open(filepath, "w") as f:
            f.write(code)

        return {
            "status": "success",
            "filename": filepath,
            "message": f"Code saved to '{filepath}'.",
            "content": code,
        }

    except Exception as e:
        return {"status": "error", "filename": None, "message": str(e), "content": None}


def summarize(transcribed_text: str) -> dict:
    """
    Summarizes the given topic or text using Groq LLM.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise summarizer. "
                        "Summarize the user's topic or text clearly in 3-5 sentences. "
                        "Use plain language. No bullet points."
                    ),
                },
                {"role": "user", "content": transcribed_text},
            ],
            temperature=0.4,
            max_tokens=300,
        )

        summary = response.choices[0].message.content.strip()
        return {
            "status": "success",
            "filename": None,
            "message": "Summary generated.",
            "content": summary,
        }

    except Exception as e:
        return {"status": "error", "filename": None, "message": str(e), "content": None}


def general_chat(transcribed_text: str, chat_history: list) -> dict:
    """
    Handles general conversation with memory of the current session.
    chat_history is a list of {"role": ..., "content": ...} dicts.
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful, friendly AI assistant. "
                    "Keep responses concise and conversational. "
                    "You have memory of this session's conversation."
                ),
            }
        ] + chat_history + [{"role": "user", "content": transcribed_text}]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=400,
        )

        reply = response.choices[0].message.content.strip()
        return {
            "status": "success",
            "filename": None,
            "message": "Response generated.",
            "content": reply,
        }

    except Exception as e:
        return {"status": "error", "filename": None, "message": str(e), "content": None}




def _parse_filename(text: str) -> str | None:
    """Tries to extract a filename from extracted_info string."""
    match = re.search(r"filename[:\s]+([^\s,]+)", text, re.IGNORECASE)
    return match.group(1) if match else None


def _parse_language(text: str) -> str | None:
    """Tries to extract a programming language from extracted_info string."""
    match = re.search(r"language[:\s]+(\w+)", text, re.IGNORECASE)
    return match.group(1).lower() if match else None


def _language_to_extension(language: str) -> str:
    mapping = {
        "python": ".py", "javascript": ".js", "typescript": ".ts",
        "java": ".java", "c": ".c", "cpp": ".cpp", "go": ".go",
        "rust": ".rs", "html": ".html", "css": ".css", "bash": ".sh",
    }
    return mapping.get(language.lower(), ".txt")


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")