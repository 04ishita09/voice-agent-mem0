# 🎙️ Voice Agent

A modern, fast, voice-controlled AI agent built with **Streamlit** and powered by **Groq** for lightning-fast inference. The agent listens to your voice (or uploaded audio files), understands your intent, and performs actions like writing code, summarizing text, creating files, or engaging in general conversation.

##  Setup Instructions

1. **Prerequisites**: Make sure you have Python 3.9+ installed.
2. **Clone the repository** (if not already downloaded):
   ```bash
   git clone <your-github-repo-link>
   cd mem0
   ```
3. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
6. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   *The app should automatically open in your browser at `http://localhost:8501`.*

## Architecture Explanation

The application follows a modular, 4-stage pipeline orchestrated by a **Streamlit** frontend frontend.

1. **Speech-to-Text (Transcription)**:
   - Handled by `stt.py`
   - Uses the **Whisper** (`whisper-large-v3`) model to convert spoken audio into raw text strings.

2. **Intent Classification & Extraction**:
   - Handled by `intent.py`
   - Passes the transcribed text to a fine-tuned prompt using **LLaMA 3** (`llama-3.3-70b-versatile`). 
   - Classifies the user's intent into predefined categories (`create_file`, `write_code`, `summarize`, `general_chat`) and extracts structured metadata (e.g., filename, target programming language).

3. **Tool Execution (Human-in-the-loop)**:
   - Handled by `tools.py`
   - For potentially destructive or meaningful file-system operations (`create_file`, `write_code`), the UI blocks execution and asks the user for explicit confirmation before generating or saving contents to the `output/` folder.
   - For purely informational requests, the platform handles it fluidly. Code generation and chat utilize **LLaMA 3**.

4. **Response Delivery**:
   - Updates the UI with beautiful glassmorphism design, logging the event history and managing a chat memory state for contextually-aware conversational follow-ups.

##  Hardware Workarounds Used

Running State-of-the-Art (SOTA) models like **Whisper Large V3** and **LLaMA 3.3 70B** locally would normally require significant and expensive local compute (e.g., dual NVIDIA RTX 3090s/4090s or an M2 Ultra with massive amounts of unified memory).

**Workaround**: To make this voice agent capable of running on virtually *any* hardware (even without a dedicated GPU), local inference was entirely offloaded to **Groq's LPU Inference Engine**. 
By doing this via API endpoints, the application achieves real-time, low-latency responsiveness without imposing any strenuous memory or processing constraints on the local device footprint. The only local requirements are an internet connection and the means to record/transfer audio segments.
