import os
import tempfile
import streamlit as st
from stt import transcribe_audio
from intent import detect_intent
from tools import create_file, write_code, summarize, general_chat

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Voice Agent",
    page_icon="🎙️",
    layout="centered",
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Background and global elements */
    .stApp {
        background-color: #fafafa;
        background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,0.04) 0, transparent 50%), 
                          radial-gradient(at 50% 0%, hsla(225,39%,30%,0.04) 0, transparent 50%), 
                          radial-gradient(at 100% 0%, hsla(339,49%,30%,0.04) 0, transparent 50%);
    }

    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }

    .step-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: slideUp 0.4s ease forwards;
        opacity: 0;
    }
    .step-card:nth-child(1) { animation-delay: 0.1s; }
    .step-card:nth-child(2) { animation-delay: 0.2s; }
    .step-card:nth-child(3) { animation-delay: 0.3s; }
    
    .step-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .step-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #6366f1;
        margin-bottom: 8px;
    }
    
    .step-value { 
        color: #1e293b; 
        font-size: 16px; 
        line-height: 1.6; 
        font-weight: 400;
    }

    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-shadow: 0 1px 1px rgba(0,0,0,0.1);
    }
    .badge-create  { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; }
    .badge-code    { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; }
    .badge-summary { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
    .badge-chat    { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; }
    .badge-error   { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; }

    .code-output {
        background: #0f172a;
        color: #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 14px;
        overflow-x: auto;
        white-space: pre-wrap;
        line-height: 1.6;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        margin-top: 10px;
    }
    .code-output::before {
        content: '';
        display: block;
        height: 10px;
        width: 10px;
        border-radius: 50%;
        background: #fc625d;
        box-shadow: 18px 0 0 #fdbc40, 36px 0 0 #35cd4b;
        margin-bottom: 16px;
    }

    .history-item {
        background: rgba(255,255,255,0.6);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 12px;
        font-size: 14px;
        color: #475569;
        transition: all 0.2s ease;
    }
    .history-item:hover {
        background: white;
        border-color: #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    .chat-user {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
        border-radius: 16px 16px 4px 16px;
        padding: 12px 18px;
        margin: 8px 0 16px auto;
        max-width: 85%;
        font-size: 15px;
        color: white;
        text-align: right;
        animation: scaleIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        transform-origin: bottom right;
    }
    
    .chat-assistant {
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        border-radius: 16px 16px 16px 4px;
        padding: 12px 18px;
        margin: 8px auto 16px 0;
        max-width: 85%;
        font-size: 15px;
        color: #334155;
        animation: scaleIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        transform-origin: bottom left;
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }

    .chat-label {
        font-size: 11px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 2px;
    }
    
    /* Streamlit overrides */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[data-baseweb="button"] {
        background: white;
        border: 1px solid #e2e8f0;
    }
    div.stButton > button[data-baseweb="button"]:hover {
        border-color: #6366f1;
        color: #6366f1;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.1);
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 8px -1px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)


# ── session state init ────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []       # for LLM memory (all intents)

if "action_log" not in st.session_state:
    st.session_state.action_log = []         # for session history sidebar

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None   # for human-in-the-loop confirmation

if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = None   # stores transcript+intent while waiting


# ── header ────────────────────────────────────────────────────────────────────
st.markdown("<h1 class='header-title'>🎙️ Voice Agent</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#64748b;font-size:16px;margin-top:-12px;font-weight:400;'>"
    "Speak or upload audio — the agent will transcribe, understand, and act.</p>",
    unsafe_allow_html=True,
)
st.divider()


# ── input section ─────────────────────────────────────────────────────────────
input_mode = st.radio(
    "Input method",
    ["Upload audio file", "Record from microphone"],
    horizontal=True,
    label_visibility="collapsed",
)

audio_path = None

if input_mode == "Upload audio file":
    uploaded = st.file_uploader(
        "Upload a .wav or .mp3 file",
        type=["wav", "mp3", "m4a", "ogg"],
        label_visibility="visible",
    )
    if uploaded:
        suffix = os.path.splitext(uploaded.name)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            audio_path = tmp.name
        st.audio(uploaded)

else:
    audio_bytes = st.audio_input("Click to record")
    if audio_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes.read())
            audio_path = tmp.name


# ── run button ────────────────────────────────────────────────────────────────
run_clicked = st.button("▶  Run Agent", type="primary", use_container_width=True)


# ── human-in-the-loop confirmation (shown when a file action is pending) ──────
if st.session_state.pending_action:
    pa = st.session_state.pending_action
    st.warning(
        f"⚠️ **Confirm action:** {pa['action_label']} — `{pa['info']}`"
    )
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, proceed", use_container_width=True):
            # execute the confirmed action
            if pa["intent"] == "create_file":
                result = create_file(pa["info"])
                action_taken = "Created file/folder"
            elif pa["intent"] == "write_code":
                result = write_code(pa["transcript"], pa["info"])
                action_taken = "Generated and saved code"

            # add to memory
            st.session_state.chat_history.append({
                "role": "user", "content": pa["transcript"]
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result.get("message", "Done.")
            })

            # log it
            st.session_state.action_log.append({
                "transcript": pa["transcript"],
                "intent": pa["intent"].replace("_", " ").title(),
                "action": action_taken,
                "status": result["status"],
            })

            st.session_state.pending_action = None
            st.session_state.pipeline_state = None

            if result["status"] == "error":
                st.error(f"Something went wrong: {result['message']}")
            else:
                st.success(result["message"])
                if result.get("content"):
                    st.markdown(
                        f"<div class='code-output'>{result['content']}</div>",
                        unsafe_allow_html=True,
                    )
            st.rerun()

    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.pending_action = None
            st.session_state.pipeline_state = None
            st.info("Action cancelled.")
            st.rerun()


# ── main pipeline ─────────────────────────────────────────────────────────────
if run_clicked and audio_path:
    st.divider()
    st.markdown("### Pipeline output")

    # stage 1 — transcription
    with st.spinner("Transcribing audio..."):
        transcript = transcribe_audio(audio_path)

    st.markdown(f"""
    <div class='step-card'>
        <div class='step-label'>01 — Transcription</div>
        <div class='step-value'>"{transcript}"</div>
    </div>
    """, unsafe_allow_html=True)

    if transcript.startswith("[ERROR]"):
        st.error(transcript)
        st.stop()

    # stage 2 — intent detection
    with st.spinner("Detecting intent..."):
        intent_result = detect_intent(transcript)

    intent     = intent_result["intent"]
    confidence = intent_result["confidence"]
    info       = intent_result["extracted_info"]

    badge_class = {
        "create_file":  "badge-create",
        "write_code":   "badge-code",
        "summarize":    "badge-summary",
        "general_chat": "badge-chat",
    }.get(intent, "badge-error")

    intent_label = intent.replace("_", " ").title()

    st.markdown(f"""
    <div class='step-card'>
        <div class='step-label'>02 — Intent</div>
        <div class='step-value'>
            <span class='badge {badge_class}'>{intent_label}</span>
            <span style='color:#888;font-size:13px'>confidence: {confidence}</span>
            <br><span style='color:#555;font-size:13px;margin-top:4px;display:block'>{info}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # stage 3 — tool execution
    with st.spinner("Executing action..."):

        # ── file operations → ask for confirmation first ──────────────────────
        if intent in ("create_file", "write_code"):
            action_labels = {
                "create_file": "Create file/folder",
                "write_code":  "Generate and save code",
            }
            st.session_state.pending_action = {
                "intent":       intent,
                "transcript":   transcript,
                "info":         info,
                "action_label": action_labels[intent],
            }
            st.session_state.pipeline_state = {
                "transcript": transcript,
                "intent":     intent_label,
            }
            st.rerun()   # re-render to show confirmation prompt

        
        elif intent == "summarize":
            result = summarize(transcript)
            action_taken = "Generated summary"

            # add to memory so future chat can reference it
            st.session_state.chat_history.append({"role": "user", "content": transcript})
            if result["status"] == "success":
                st.session_state.chat_history.append({
                    "role": "assistant", "content": result["content"]
                })

        
        else:
            result = general_chat(transcript, st.session_state.chat_history)
            action_taken = "Chat response"
            st.session_state.chat_history.append({"role": "user", "content": transcript})
            if result["status"] == "success":
                st.session_state.chat_history.append({
                    "role": "assistant", "content": result["content"]
                })

    # stage 3 card (only for non-file intents — file intents rerun above)
    if intent not in ("create_file", "write_code"):
        st.markdown(f"""
        <div class='step-card'>
            <div class='step-label'>03 — Action taken</div>
            <div class='step-value'>{action_taken}</div>
        </div>
        """, unsafe_allow_html=True)

        # stage 4 — output
        if result["status"] == "error":
            st.error(f"Something went wrong: {result['message']}")
        else:
            st.markdown("<div class='step-label' style='margin-top:8px'>04 — Output</div>", unsafe_allow_html=True)
            if result.get("content"):
                st.success(result["content"])
            else:
                st.success(result["message"])

        # log
        st.session_state.action_log.append({
            "transcript": transcript,
            "intent": intent_label,
            "action": action_taken,
            "status": result["status"],
        })

elif run_clicked and not audio_path:
    st.warning("Please upload or record audio first.")


if st.session_state.chat_history:
    st.divider()
    st.markdown("### 💬 Conversation memory")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='chat-label' style='text-align:right'>You</div>
            <div class='chat-user'>{msg['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-label'>Agent</div>
            <div class='chat-assistant'>{msg['content']}</div>
            """, unsafe_allow_html=True)



if st.session_state.action_log:
    st.divider()
    st.markdown("### Session history")
    for entry in reversed(st.session_state.action_log):
        status_icon = "✅" if entry["status"] == "success" else "❌"
        st.markdown(f"""
        <div class='history-item'>
            {status_icon} <strong>{entry['intent']}</strong> &nbsp;·&nbsp; {entry['action']}<br>
            <span style='color:#999'>{entry['transcript'][:80]}{"..." if len(entry['transcript']) > 80 else ""}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Clear history"):
        st.session_state.action_log = []
        st.session_state.chat_history = []
        st.rerun()