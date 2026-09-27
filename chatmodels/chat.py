import streamlit as st
import textwrap
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel
from typing import List, Optional


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Nova · AI Assistant",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# MODEL
# =========================================================
model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    max_retries=3
)


# =========================================================
# MOVIE DATA MODEL
# =========================================================

class Movie(BaseModel):
    title: str
    release_year: Optional[int] = None
    director: List[str]
    rating: Optional[float] = None
    summary: str


parser = PydanticOutputParser(pydantic_object=Movie)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "funny"

if "page" not in st.session_state:
    st.session_state.page = "chat"


MODES = {
    "angry": {
        "emoji": "😡",
        "label": "Angry",
        "accent": "#ff6b6b",
        "accent_soft": "rgba(255,107,107,.14)",
        "system": "You are an angry AI agent. You respond aggressively and impatiently.",
        "desc": "Blunt, sharp, no patience",
    },
    "funny": {
        "emoji": "😂",
        "label": "Funny",
        "accent": "#ffc94d",
        "accent_soft": "rgba(255,201,77,.14)",
        "system": "You are a very funny AI agent. You respond with humor and jokes.",
        "desc": "Witty, playful, joke-filled",
    },
    "sad": {
        "emoji": "😢",
        "label": "Sad",
        "accent": "#6ea8ff",
        "accent_soft": "rgba(110,168,255,.14)",
        "system": "You are a very sad AI agent. You respond in a depressed and emotional tone.",
        "desc": "Gloomy, emotional, melancholic",
    },
}


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    textwrap.dedent("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Manrope:wght@600;700;800&display=swap');

* { box-sizing: border-box; }

:root {
    --bg: #0a0a0f;
    --bg-2: #0e0e16;
    --card: #14141e;
    --card-2: #191926;
    --border: rgba(255,255,255,.08);
    --text: #f2f2f7;
    --muted: #8b8b9c;
    --violet: #8b5cf6;
    --violet-2: #6366f1;
    --pink: #ec4899;
    --grad: linear-gradient(135deg, #8b5cf6, #6366f1 55%, #ec4899);
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 15% 0%, rgba(139,92,246,.18), transparent 40%),
        radial-gradient(circle at 90% 20%, rgba(236,72,153,.12), transparent 45%),
        radial-gradient(circle at 50% 100%, rgba(99,102,241,.10), transparent 50%),
        var(--bg);
    color: var(--text);
    overflow-x: hidden;
}

#MainMenu, footer, header { visibility: hidden; }

.main .block-container { animation: fadeUp .45s cubic-bezier(.2,.8,.2,1); }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,.35); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,.55); }

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d16 0%, #0a0a10 100%);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div { padding: 22px 16px; }

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 4px 22px;
}

.brand-mark {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    background: var(--grad);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 10px 28px rgba(139,92,246,.35);
}

.brand-name {
    font-family: 'Manrope', sans-serif;
    font-size: 17px;
    font-weight: 800;
    color: #fff;
    letter-spacing: -.3px;
}

.brand-sub {
    font-size: 11px;
    color: var(--muted);
    margin-top: 1px;
}

.side-label {
    color: #6c6c7c;
    text-transform: uppercase;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.3px;
    padding: 18px 4px 10px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 13px;
    border-radius: 12px;
    margin-bottom: 5px;
    font-size: 13px;
    font-weight: 600;
    color: #b5b5c4;
    border: 1px solid transparent;
    cursor: pointer;
    transition: .15s ease;
}

.nav-item:hover { background: rgba(255,255,255,.04); }

.nav-item.active {
    background: linear-gradient(135deg, rgba(139,92,246,.16), rgba(236,72,153,.10));
    border-color: rgba(139,92,246,.3);
    color: #fff;
}

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    justify-content: flex-start;
    text-align: left;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    color: #b5b5c4;
    padding: 11px 13px;
    min-height: 0;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,.04);
    border-color: var(--border);
    color: #fff;
    transform: none;
}

section[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
    border-color: rgba(139,92,246,.3);
}

.nav-active-btn > button {
    background: linear-gradient(135deg, rgba(139,92,246,.18), rgba(236,72,153,.10)) !important;
    border-color: rgba(139,92,246,.35) !important;
    color: #fff !important;
}

.mood-card {
    border-radius: 14px;
    border: 1px solid var(--border);
    padding: 12px;
    margin-top: 6px;
    background: rgba(255,255,255,.02);
}

.mood-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 9px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 600;
    color: #a9a9ba;
    cursor: pointer;
    transition: .15s ease;
    margin-bottom: 3px;
}

.mood-row.selected {
    color: #fff;
}

.sidebar-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 16px 0;
    border: 0;
}

.footnote {
    color: #4d4d5c;
    font-size: 10px;
    text-align: center;
    margin-top: 14px;
}

/* ---------- MAIN LAYOUT ---------- */

.block-container { max-width: 1500px; padding: 0 34px 120px; }

.topbar {
    height: 76px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    margin-bottom: 30px;
}

.topbar-left { display: flex; align-items: center; gap: 12px; }

.page-title {
    font-family: 'Manrope', sans-serif;
    font-size: 17px;
    font-weight: 800;
    color: #fff;
}

.page-sub { font-size: 11px; color: var(--muted); margin-top: 1px; }

.chip {
    border-radius: 20px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid;
}

.chip-model {
    color: #b39dfb;
    border-color: rgba(139,92,246,.3);
    background: rgba(139,92,246,.10);
}

/* ---------- HERO ---------- */

.hero { max-width: 780px; margin: 30px auto 18px; text-align: center; }

.hero-badge {
    width: 56px;
    height: 56px;
    margin: 0 auto 20px;
    border-radius: 18px;
    background: var(--grad);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    box-shadow: 0 16px 36px rgba(139,92,246,.35);
}

.hero h1 {
    margin: 0;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(28px, 4.6vw, 44px);
    letter-spacing: -1.4px;
    font-weight: 800;
    background: linear-gradient(180deg, #ffffff, #b9b9cc);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero p {
    color: var(--muted);
    font-size: 13.5px;
    line-height: 1.7;
    max-width: 540px;
    margin: 12px auto 0;
}

/* ---------- MODE PICKER (main area, welcome screen) ---------- */

.mode-grid {
    max-width: 780px;
    margin: 28px auto 8px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

/* ---------- SUGGESTIONS ---------- */

.sugg-label {
    max-width: 780px;
    margin: 22px auto 10px;
    color: var(--muted);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    text-align: center;
}

/* ---------- CHAT MESSAGES ---------- */

[data-testid="stChatMessage"] {
    background: transparent !important;
    border: 0 !important;
    padding: 7px 0 !important;
    animation: msgIn .28s cubic-bezier(.2,.8,.2,1);
}

@keyframes msgIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    font-size: 14px;
    line-height: 1.7;
}

[data-testid="stChatMessageContent"] {
    border-radius: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,.25);
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { justify-content: flex-end; }

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(150deg, #6d3fd6, #4f3fc9);
    border: 1px solid rgba(139,92,246,.35);
    color: #fff;
    max-width: 76%;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: var(--card);
    border: 1px solid var(--border);
    max-width: 80%;
}

[data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {
    box-shadow: 0 6px 16px rgba(0,0,0,.35);
}

/* ---------- CHAT INPUT ---------- */

[data-testid="stChatInput"] { max-width: 780px; margin: 22px auto 0; }

[data-testid="stChatInput"] > div {
    background: #f4f2fb !important;
    border: 0 !important;
    border-radius: 18px !important;
    box-shadow: 0 16px 40px rgba(0,0,0,.3);
    transition: box-shadow .2s ease;
}

[data-testid="stChatInput"] > div:focus-within {
    box-shadow: 0 16px 40px rgba(139,92,246,.25), 0 0 0 2px rgba(139,92,246,.4);
}

[data-testid="stChatInput"] textarea { color: #16161f !important; font-size: 13.5px !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #8f8fa0 !important; }

/* ---------- BUTTONS (main area) ---------- */

.stButton > button {
    border-radius: 12px;
    border: 1px solid var(--border);
    background: var(--card);
    color: #d3d3e0;
    min-height: 42px;
    transition: .18s ease;
}

.stButton > button:hover {
    border-color: rgba(139,92,246,.4);
    color: #fff;
    background: var(--card-2);
    transform: translateY(-2px);
}

.stButton > button[kind="primary"] {
    background: var(--grad);
    color: #fff;
    border: 0;
    font-weight: 700;
    box-shadow: 0 10px 26px rgba(139,92,246,.32);
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 14px 32px rgba(139,92,246,.42);
    transform: translateY(-2px);
}

/* ---------- TEXTAREA (movie input) ---------- */

.stTextArea textarea {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    color: #f0f0f7 !important;
    font-size: 13.5px !important;
    line-height: 1.65 !important;
}

.stTextArea textarea:focus {
    border-color: rgba(139,92,246,.45) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,.14) !important;
}

/* ---------- MOVIE PAGE ---------- */

.movie-shell { max-width: 980px; margin: 26px auto 16px; }

.movie-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(26px, 3.6vw, 38px);
    font-weight: 800;
    letter-spacing: -1px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.movie-subtitle { color: var(--muted); font-size: 13px; line-height: 1.6; margin: 8px 0 4px; }

.movie-input-shell { max-width: 980px; margin: 0 auto 18px; }

.movie-results { max-width: 980px; margin: 0 auto; }

.movie-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px 24px;
    margin-top: 14px;
    transition: .2s ease;
}

.movie-card:hover { border-color: rgba(139,92,246,.28); transform: translateY(-2px); }

.movie-card.hero-card {
    background: linear-gradient(135deg, rgba(139,92,246,.16), rgba(20,20,30,.9) 60%);
    border-color: rgba(139,92,246,.28);
}

.result-label {
    color: #9a9aac;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.result-value { color: #f5f5fb; font-size: 18px; font-weight: 700; margin-top: 6px; }

.summary-text { color: #cfcfdd; line-height: 1.8; margin-top: 10px; font-size: 14px; }

/* ---------- MOBILE ---------- */

@media (max-width: 900px) {
    .block-container { padding: 0 18px 110px; }
    .mode-grid { grid-template-columns: 1fr; max-width: 480px; }
    .hero h1 { font-size: 30px; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
        max-width: 92%;
    }
}

@media (max-width: 600px) {
    section[data-testid="stSidebar"] { width: 280px !important; }
    .block-container { padding: 0 12px 105px; }
    .topbar { height: 60px; }
    .hero h1 { font-size: 25px; letter-spacing: -1px; }
    .hero-badge { width: 46px; height: 46px; }
    .movie-card { padding: 16px; }
}

</style>
"""),
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">🪐</div>
            <div>
                <div class="brand-name">Nova</div>
                <div class="brand-sub">AI Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Workspace</div>', unsafe_allow_html=True)

    nav_items = [("chat", "💬", "AI Chat"), ("movie", "🎬", "Movie Info")]

    for key, icon, label in nav_items:
        is_active = st.session_state.page == key
        wrapper_class = "nav-active-btn" if is_active else ""
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-label">AI Personality</div>', unsafe_allow_html=True)

    st.markdown('<div class="mood-card">', unsafe_allow_html=True)

    for key, m in MODES.items():
        is_sel = st.session_state.mode == key
        label = f"{m['emoji']}  {m['label']} — {m['desc']}" if is_sel else f"{m['emoji']}  {m['label']}"
        if st.button(label, key=f"mode_{key}", use_container_width=True):
            st.session_state.mode = key
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="footnote">Nova · Your personal AI workspace</div>', unsafe_allow_html=True)


# =========================================================
# AI CHAT PAGE
# =========================================================

if st.session_state.page == "chat":

    active_mode = MODES[st.session_state.mode]
    system_prompt = active_mode["system"]

    # Top bar
    st.markdown(
        f"""
        <div class="topbar">
            <div class="topbar-left">
                <div>
                    <div class="page-title">AI Chat</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.messages:
        c1, c2 = st.columns([9, 1])
        with c2:
            if st.button("🗑️", help="Clear chat"):
                st.session_state.messages = []
                st.rerun()

    clicked_suggestion = None

    if not st.session_state.messages:

        st.markdown(
            f"""
            <div class="hero">
                <div class="hero-badge">🪐</div>
                <h1>How can I help you today?</h1>
                <p>
                    Your personal AI workspace for ideas, questions,
                    coding, learning and everyday conversations —
                </p>
            </div>
            <div class="sugg-label">Try asking</div>
            """,
            unsafe_allow_html=True,
        )

        suggestions = [
            "Explain quantum computing simply",
            "Search movie details",
            "Give me 3 productivity tips",
            "How to improve personality",
        ]

        sug_cols = st.columns(4)
        for i, s in enumerate(suggestions):
            with sug_cols[i]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    clicked_suggestion = s

    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user", avatar="🧑"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant", avatar="🪐"):
                st.markdown(message.content)

    user_input = st.chat_input("Type your prompt here...")

    if clicked_suggestion:
        user_input = clicked_suggestion

    if user_input:

        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)

        messages = [SystemMessage(content=system_prompt)]
        messages.extend(st.session_state.messages[-6:])
        messages.append(HumanMessage(content=user_input))

        with st.chat_message("assistant", avatar="🪐"):
            with st.spinner("Thinking..."):
                try:
                    response = model.invoke(messages)

                    if isinstance(response.content, list):
                        answer = "".join(
                            item.get("text", "")
                            for item in response.content
                            if isinstance(item, dict) and item.get("type") == "text"
                        )
                    else:
                        answer = response.content

                    st.markdown(answer)

                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        st.warning("The assistant is temporarily busy. Please try again in a few seconds.")
                    else:
                        st.error(f"Something went wrong:\n\n{e}")
                    answer = None

        if answer:
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.session_state.messages.append(AIMessage(content=answer))
            st.rerun()


# =========================================================
# MOVIE INFORMATION EXTRACTOR PAGE
# =========================================================

elif st.session_state.page == "movie":

    st.markdown(
        """
        <div class="movie-shell">
            <div class="movie-title">🎬 Movie Information</div>
            <div class="movie-subtitle">
                Paste a movie paragraph and let AI extract structured
                information such as title, year, director, rating and summary.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="movie-input-shell">', unsafe_allow_html=True)

    paragraph = st.text_area(
        "Movie Paragraph",
        height=180,
        placeholder=(
            "Example: Inception is a 2010 science-fiction movie directed "
            "by Christopher Nolan. The movie has a rating of 8.8..."
        ),
        label_visibility="collapsed",
    )

    extract_clicked = st.button(
        "🔍  Extract Movie Information",
        type="primary",
        use_container_width=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)

    if extract_clicked:

        if not paragraph.strip():
            st.warning("Please enter a movie paragraph first.")
        else:

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        Extract movie information from the paragraph below.

                        Return the information according to the following
                        format instructions:

                        {format_instructions}

                        If some information is not available,
                        use null where appropriate.
                        """,
                    ),
                    ("human", "{paragraph}"),
                ]
            )

            final_prompt = prompt.invoke(
                {
                    "paragraph": paragraph,
                    "format_instructions": parser.get_format_instructions(),
                }
            )

            with st.spinner("Extracting movie information..."):
                try:
                    response = model.invoke(final_prompt)
                    movie_data = parser.parse(response.content)

                    st.success("Movie information extracted successfully!")

                    st.markdown('<div class="movie-results">', unsafe_allow_html=True)

                    st.markdown(
                        f"""
                        <div class="movie-card hero-card">
                            <div class="result-label">🎬 Movie title</div>
                            <div class="result-value">{movie_data.title}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(
                            f"""
                            <div class="movie-card">
                                <div class="result-label">📅 Release Year</div>
                                <div class="result-value">
                                    {movie_data.release_year or "Not available"}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="movie-card">
                                <div class="result-label">🎥 Director</div>
                                <div class="result-value">
                                    {", ".join(movie_data.director) if movie_data.director else "Not available"}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with col2:
                        rating = (
                            str(movie_data.rating)
                            if movie_data.rating is not None
                            else "Not available"
                        )
                        st.markdown(
                            f"""
                            <div class="movie-card">
                                <div class="result-label">⭐ Rating</div>
                                <div class="result-value">⭐ {rating}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <div class="result-label">📝 Summary</div>
                            <div class="summary-text">{movie_data.summary}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown('</div>', unsafe_allow_html=True)

                    with st.expander("🔧 View Structured Data"):
                        st.json(movie_data.model_dump())

                except Exception as e:
                    st.error("Could not extract the movie information.")
                    st.code(str(e))