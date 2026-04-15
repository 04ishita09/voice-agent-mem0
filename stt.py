import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def transcribe_audio(audio_path: str) -> str:
    """
    Takes a path to an audio file (.wav or .mp3),
    sends it to Groq's Whisper endpoint,
    and returns the transcribed text.
    """
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), audio_file.read()),
                model="whisper-large-v3",
                language="en",
                response_format="text",
            )
        return transcription.strip()

    except FileNotFoundError:
        return f"[ERROR] Audio file not found: {audio_path}"
    except Exception as e:
        return f"[ERROR] Transcription failed: {str(e)}"


if __name__ == "__main__":
    # quick test — drop any .wav or .mp3 here
    result = transcribe_audio("test.wav")
    print("Transcription:", result)