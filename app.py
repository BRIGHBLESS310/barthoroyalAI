from flask import Flask, request, jsonify, render_template_string
import requests
import urllib.parse
import os
import json
import time

app = Flask(__name__)

# ============================================================
# COMPANION AI
# General-purpose AI assistant
# Everything is contained in this one Python file.
# ============================================================


# ============================================================
# AI INSTRUCTIONS
# ============================================================

INSTRUCTIONS = {
    "chat": """
You are Companion AI, a helpful general-purpose AI assistant.

Answer questions clearly, naturally, and accurately.
Help with technology, coding, science, writing, creativity,
general knowledge, ideas, explanations, and everyday questions.

Do not describe yourself as a school tutor or student assistant.
Do not assume the user is a student.
Keep answers useful and easy to understand.
""",

    "codex": """
You are Codex, an expert programming and software-development AI.

Help users with:
- Python
- JavaScript
- HTML
- CSS
- Flask
- APIs
- databases
- debugging
- web development
- game development
- software architecture
- command-line problems

When useful, provide complete working code.
Explain errors clearly.
Do not assume the user is a student.
""",

    "vibe": """
You are Companion AI in Vibe mode.

Be friendly, relaxed, creative, conversational, and energetic.
Help with brainstorming, stories, ideas, names, concepts,
creative projects, jokes, designs, apps, games, and imagination.

Do not use school or student-focused language unless the user
specifically asks about it.
""",

    "video": """
You are a professional AI video-prompt creator.

When the user asks for a video, create a detailed video-generation
prompt describing:

- subject
- environment
- action
- camera movement
- camera angle
- lighting
- atmosphere
- visual style
- motion
- composition
- duration
- quality

Do not claim that you actually rendered a video.
Instead, provide a polished prompt that can be used by a video
generation system.
""",

    "explore": """
You are Companion AI's Explore assistant.

Help users discover useful ideas, tools, projects, technologies,
creative concepts, programming ideas, business ideas, game ideas,
AI workflows, and interesting topics.

Keep the response practical and organized.
""",
}


# ============================================================
# TEXT AI
# ============================================================

def pollinations_text(prompt):
    """
    Try the Pollinations text endpoint.
    """

    try:
        encoded = urllib.parse.quote(prompt)

        url = f"https://text.pollinations.ai/{encoded}"

        response = requests.get(
            url,
            timeout=45
        )

        if response.status_code == 200:
            text = response.text.strip()

            if text:
                return text

    except Exception:
        pass

    return None


def pollinations_openai(prompt):
    """
    Try the OpenAI-compatible Pollinations endpoint.
    """

    try:
        url = "https://text.pollinations.ai/openai"

        payload = {
            "model": "openai",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            url,
            json=payload,
            timeout=45
        )

        if response.status_code == 200:

            data = response.json()

            try:
                return data["choices"][0]["message"]["content"]
            except Exception:
                pass

    except Exception:
        pass

    return None


def wikipedia_answer(question):
    """
    Wikipedia fallback for basic factual questions.
    """

    try:

        encoded = urllib.parse.quote(question)

        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + encoded
        )

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "CompanionAI/1.0"
            }
        )

        if response.status_code == 200:

            data = response.json()

            extract = data.get("extract")

            if extract:
                return extract

    except Exception:
        pass

    return None


def ollama_answer(prompt):
    """
    Try a locally installed Ollama model if available.
    """

    try:

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:

            data = response.json()

            answer = data.get("response")

            if answer:
                return answer

    except Exception:
        pass

    return None


# ============================================================
# MAIN AI FUNCTION
# ============================================================

def get_answer(message, mode="chat"):

    system_instruction = INSTRUCTIONS.get(
        mode,
        INSTRUCTIONS["chat"]
    )

    full_prompt = f"""
{system_instruction}

USER MESSAGE:
{message}

Give the best helpful response.
"""

    # Try OpenAI-compatible endpoint first
    answer = pollinations_openai(full_prompt)

    if answer:
        return answer

    # Try normal text endpoint
    answer = pollinations_text(full_prompt)

    if answer:
        return answer

    # Try local Ollama
    answer = ollama_answer(full_prompt)

    if answer:
        return answer

    # Try Wikipedia
    answer = wikipedia_answer(message)

    if answer:
        return answer

    # Final fallback
    return (
        "I couldn't connect to an AI service right now. "
        "Please check your internet connection or make sure "
        "your AI service is available, then try again."
    )


# ============================================================
# IMAGE GENERATION
# ============================================================

def generate_image(prompt):

    encoded = urllib.parse.quote(
        prompt,
        safe=""
    )

    url = (
        "https://image.pollinations.ai/prompt/"
        + encoded
        + "?nologo=true"
        + "&width=1024"
        + "&height=1024"
    )

    return url


# ============================================================
# VIDEO PROMPT
# ============================================================

def generate_video_prompt(prompt):

    instruction = f"""
Create a professional AI video-generation prompt from this idea:

{prompt}

Return a polished prompt containing:

Subject:
Environment:
Action:
Camera:
Lighting:
Atmosphere:
Visual style:
Motion:
Composition:
Quality:

Make it cinematic and detailed.
"""

    answer = get_answer(
        instruction,
        "video"
    )

    return answer


# ============================================================
# SMART REQUEST
# ============================================================

def smart(message, mode):

    if mode == "image":

        image_url = generate_image(message)

        return {
            "type": "image",
            "text": "Your image is ready.",
            "image": image_url
        }

    if mode == "video":

        result = generate_video_prompt(message)

        return {
            "type": "text",
            "text": result
        }

    answer = get_answer(
        message,
        mode
    )

    return {
        "type": "text",
        "text": answer
    }


# ============================================================
# MAIN HTML
# ============================================================

UI = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Companion AI</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {

    --bg: #050505;
    --panel: #0b0b0b;
    --panel2: #101010;

    --border: rgba(255, 255, 255, 0.08);

    --text: #ffffff;
    --muted: #969696;

    --red: #ff2b2b;
    --orange: #ff6a00;
    --yellow: #ffb300;

    --glow:
        0 0 10px rgba(255, 55, 0, .5),
        0 0 25px rgba(255, 55, 0, .2);

    --radius: 18px;
}

body {

    font-family:
        Inter,
        Arial,
        Helvetica,
        sans-serif;

    background:
        radial-gradient(
            circle at top right,
            rgba(255, 70, 0, .12),
            transparent 35%
        ),
        radial-gradient(
            circle at bottom left,
            rgba(255, 0, 0, .08),
            transparent 35%
        ),
        var(--bg);

    color: var(--text);

    height: 100vh;

    overflow: hidden;
}


/* ============================================================
   APP
   ============================================================ */

.app {

    display: flex;

    height: 100vh;

    width: 100%;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

.sidebar {

    width: 270px;

    min-width: 270px;

    background:
        linear-gradient(
            180deg,
            #090909,
            #050505
        );

    border-right:
        1px solid var(--border);

    display: flex;

    flex-direction: column;

    padding: 18px;

    z-index: 20;
}


/* ============================================================
   LOGO
   ============================================================ */

.logo {

    display: flex;

    align-items: center;

    gap: 12px;

    padding:
        8px
        8px
        22px;
}

.logo-fire {

    width: 42px;

    height: 42px;

    border-radius: 14px;

    background:
        linear-gradient(
            135deg,
            #ff2200,
            #ff7600,
            #ffc400
        );

    display: flex;

    justify-content: center;

    align-items: center;

    font-size: 22px;

    box-shadow: var(--glow);

}

.logo-name {

    font-size: 20px;

    font-weight: 800;

    letter-spacing: .5px;
}


/* ============================================================
   NAV
   ============================================================ */

.nav {

    display: flex;

    flex-direction: column;

    gap: 7px;

    flex: 1;
}

.nav-button {

    border: 1px solid transparent;

    background: transparent;

    color: #bcbcbc;

    width: 100%;

    padding: 12px;

    border-radius: 13px;

    cursor: pointer;

    display: flex;

    align-items: center;

    gap: 12px;

    text-align: left;

    font-size: 14px;

    transition: .2s ease;
}

.nav-button:hover {

    background:
        rgba(255, 72, 0, .09);

    color: white;

    border-color:
        rgba(255, 72, 0, .15);

    transform: translateX(2px);
}

.nav-button.active {

    background:
        linear-gradient(
            90deg,
            rgba(255, 55, 0, .20),
            rgba(255, 55, 0, .05)
        );

    color: white;

    border-color:
        rgba(255, 65, 0, .28);

    box-shadow:
        inset 3px 0 0 var(--orange);
}

.nav-icon {

    width: 25px;

    text-align: center;

    font-size: 17px;
}


/* ============================================================
   ACCOUNT
   ============================================================ */

.account {

    border-top:
        1px solid var(--border);

    padding-top: 16px;

    display: flex;

    align-items: center;

    gap: 10px;
}

.avatar {

    width: 38px;

    height: 38px;

    border-radius: 50%;

    background:
        linear-gradient(
            135deg,
            #ff2400,
            #ff8500
        );

    display: flex;

    align-items: center;

    justify-content: center;

    font-weight: 800;

    box-shadow:
        0 0 15px
        rgba(255, 70, 0, .3);
}

.account-name {

    font-size: 13px;

    font-weight: 700;
}

.account-status {

    font-size: 11px;

    color: #888;

    margin-top: 2px;
}


/* ============================================================
   MAIN
   ============================================================ */

.main {

    flex: 1;

    min-width: 0;

    display: flex;

    flex-direction: column;

    position: relative;
}


/* ============================================================
   TOP BAR
   ============================================================ */

.topbar {

    height: 66px;

    min-height: 66px;

    border-bottom:
        1px solid var(--border);

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding:
        0
        22px;

    background:
        rgba(5,5,5,.85);

    backdrop-filter: blur(15px);

    z-index: 10;
}

.top-title {

    display: flex;

    align-items: center;

    gap: 10px;

    font-weight: 750;
}

.online {

    display: flex;

    align-items: center;

    gap: 7px;

    font-size: 11px;

    color: #79ff8b;
}

.online-dot {

    width: 7px;

    height: 7px;

    background: #39ff63;

    border-radius: 50%;

    box-shadow:
        0 0 10px #39ff63;
}


/* ============================================================
   MOBILE MENU
   ============================================================ */

.mobile-menu {

    display: none;

    border: 1px solid var(--border);

    background: #111;

    color: white;

    width: 40px;

    height: 40px;

    border-radius: 12px;

    cursor: pointer;

    font-size: 19px;
}


/* ============================================================
   CONTENT
   ============================================================ */

.content {

    flex: 1;

    overflow-y: auto;

    padding: 30px;

    scroll-behavior: smooth;
}

.page {

    display: none;

    max-width: 1000px;

    margin: auto;

    min-height: 100%;
}

.page.active {

    display: block;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {

    min-height:
        calc(100vh - 160px);

    display: flex;

    align-items: center;

    justify-content: center;

    text-align: center;

    flex-direction: column;
}

.hero-logo {

    width: 75px;

    height: 75px;

    border-radius: 24px;

    background:
        linear-gradient(
            135deg,
            #ff1900,
            #ff6500,
            #ffc000
        );

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 38px;

    margin-bottom: 22px;

    box-shadow:
        0 0 20px rgba(255,70,0,.6),
        0 0 60px rgba(255,40,0,.2);
}

.hero h1 {

    font-size:
        clamp(30px, 5vw, 52px);

    line-height: 1.05;

    margin-bottom: 15px;
}

.gradient-text {

    background:
        linear-gradient(
            90deg,
            #fff,
            #ff6a00,
            #ff2600
        );

    -webkit-background-clip: text;

    background-clip: text;

    color: transparent;
}

.hero p {

    color: var(--muted);

    max-width: 620px;

    line-height: 1.7;

    margin-bottom: 30px;
}


/* ============================================================
   CHAT
   ============================================================ */

.chat-page {

    height: calc(100vh - 126px);

    display: flex;

    flex-direction: column;
}

.chat-header {

    margin-bottom: 18px;
}

.chat-header h2 {

    font-size: 26px;

    margin-bottom: 6px;
}

.chat-header p {

    color: var(--muted);

    font-size: 13px;
}

.messages {

    flex: 1;

    overflow-y: auto;

    padding:
        10px
        0
        25px;

    display: flex;

    flex-direction: column;

    gap: 18px;
}

.message {

    display: flex;

    gap: 12px;

    max-width: 850px;
}

.message.user {

    margin-left: auto;

    flex-direction: row-reverse;
}

.message-avatar {

    width: 36px;

    min-width: 36px;

    height: 36px;

    border-radius: 12px;

    display: flex;

    align-items: center;

    justify-content: center;

    background:
        #151515;

    border:
        1px solid var(--border);
}

.message.user .message-avatar {

    background:
        linear-gradient(
            135deg,
            #ff2700,
            #ff7800
        );
}

.bubble {

    padding: 13px 16px;

    border-radius: 16px;

    background:
        #101010;

    border:
        1px solid var(--border);

    line-height: 1.65;

    font-size: 14px;

    white-space: pre-wrap;

    max-width: min(760px, 75vw);
}

.message.user .bubble {

    background:
        linear-gradient(
            135deg,
            rgba(255,55,0,.18),
            rgba(255,110,0,.08)
        );

    border-color:
        rgba(255,70,0,.22);
}


/* ============================================================
   COMPOSER
   ============================================================ */

.composer-area {

    padding-top: 8px;

    border-top:
        1px solid var(--border);
}

.composer {

    display: flex;

    align-items: flex-end;

    gap: 10px;

    background:
        #0d0d0d;

    border:
        1px solid #252525;

    border-radius: 18px;

    padding: 10px;

    transition: .2s;
}

.composer:focus-within {

    border-color:
        rgba(255,70,0,.5);

    box-shadow:
        0 0 20px
        rgba(255,60,0,.08);
}

textarea {

    flex: 1;

    resize: none;

    border: none;

    outline: none;

    background: transparent;

    color: white;

    min-height: 42px;

    max-height: 160px;

    padding: 11px;

    font-family: inherit;

    font-size: 14px;
}

textarea::placeholder {

    color: #666;
}

.send-button {

    width: 45px;

    height: 45px;

    border: none;

    border-radius: 14px;

    background:
        linear-gradient(
            135deg,
            #ff2200,
            #ff7600
        );

    color: white;

    cursor: pointer;

    font-size: 18px;

    box-shadow:
        0 0 15px
        rgba(255,70,0,.25);

    transition: .2s;
}

.send-button:hover {

    transform: scale(1.05);

    box-shadow:
        0 0 25px
        rgba(255,70,0,.5);
}

.send-button:disabled {

    opacity: .5;

    cursor: not-allowed;
}

.status {

    text-align: center;

    color: #666;

    font-size: 11px;

    padding: 8px;
}


/* ============================================================
   QUICK ACTIONS
   ============================================================ */

.quick-actions {

    display: flex;

    gap: 8px;

    overflow-x: auto;

    padding:
        12px
        0
        4px;
}

.quick-button {

    white-space: nowrap;

    border:
        1px solid #242424;

    background:
        #0d0d0d;

    color: #aaa;

    padding:
        9px
        12px;

    border-radius: 12px;

    cursor: pointer;

    font-size: 12px;

    transition: .2s;
}

.quick-button:hover {

    color: white;

    border-color:
        rgba(255,70,0,.4);

    background:
        rgba(255,70,0,.08);
}


/* ============================================================
   CARDS
   ============================================================ */

.section-title {

    font-size: 30px;

    margin-bottom: 8px;
}

.section-description {

    color: var(--muted);

    margin-bottom: 25px;

    line-height: 1.6;
}

.grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(220px, 1fr)
        );

    gap: 15px;
}

.card {

    background:
        linear-gradient(
            145deg,
            #111,
            #090909
        );

    border:
        1px solid var(--border);

    border-radius: 18px;

    padding: 20px;

    cursor: pointer;

    transition: .2s;
}

.card:hover {

    transform: translateY(-3px);

    border-color:
        rgba(255,70,0,.35);

    box-shadow:
        0 10px 35px
        rgba(0,0,0,.35);
}

.card-icon {

    font-size: 26px;

    margin-bottom: 15px;
}

.card h3 {

    font-size: 16px;

    margin-bottom: 7px;
}

.card p {

    color: #888;

    line-height: 1.5;

    font-size: 13px;
}


/* ============================================================
   IMAGE PAGE
   ============================================================ */

.image-box {

    max-width: 750px;
}

.big-input {

    width: 100%;

    min-height: 130px;

    background:
        #0d0d0d;

    border:
        1px solid #252525;

    border-radius: 18px;

    padding: 18px;

    color: white;

    outline: none;

    resize: vertical;

    font-family: inherit;

    margin-bottom: 12px;
}

.primary-button {

    border: none;

    border-radius: 13px;

    padding:
        12px
        18px;

    background:
        linear-gradient(
            135deg,
            #ff2100,
            #ff7800
        );

    color: white;

    font-weight: 700;

    cursor: pointer;

    box-shadow:
        0 0 20px
        rgba(255,70,0,.2);
}

.primary-button:hover {

    filter: brightness(1.12);
}

.generated-image {

    margin-top: 25px;

    width: 100%;

    border-radius: 20px;

    border:
        1px solid var(--border);

    display: none;
}


/* ============================================================
   LIBRARY
   ============================================================ */

.library-list {

    display: flex;

    flex-direction: column;

    gap: 10px;
}

.library-item {

    background:
        #0e0e0e;

    border:
        1px solid var(--border);

    border-radius: 15px;

    padding: 15px;

    cursor: pointer;
}

.library-item:hover {

    border-color:
        rgba(255,70,0,.35);
}

.library-title {

    font-weight: 700;

    margin-bottom: 5px;

    white-space: nowrap;

    overflow: hidden;

    text-overflow: ellipsis;
}

.library-date {

    font-size: 11px;

    color: #666;
}

.empty {

    color: #666;

    padding: 35px;

    text-align: center;

    border:
        1px dashed #252525;

    border-radius: 15px;
}


/* ============================================================
   SETTINGS
   ============================================================ */

.setting {

    background:
        #0e0e0e;

    border:
        1px solid var(--border);

    padding: 18px;

    border-radius: 15px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    margin-bottom: 10px;
}

.setting h3 {

    font-size: 14px;

    margin-bottom: 4px;
}

.setting p {

    font-size: 12px;

    color: #777;
}

.toggle {

    width: 48px;

    height: 26px;

    border-radius: 20px;

    background: #292929;

    position: relative;

    cursor: pointer;
}

.toggle.on {

    background:
        linear-gradient(
            90deg,
            #ff2600,
            #ff7900
        );
}

.toggle-circle {

    width: 20px;

    height: 20px;

    border-radius: 50%;

    background: white;

    position: absolute;

    top: 3px;

    left: 4px;

    transition: .2s;
}

.toggle.on .toggle-circle {

    left: 24px;
}


/* ============================================================
   TOAST
   ============================================================ */

.toast {

    position: fixed;

    bottom: 25px;

    right: 25px;

    background:
        #151515;

    border:
        1px solid rgba(255,70,0,.3);

    box-shadow:
        0 10px 35px rgba(0,0,0,.5);

    border-radius: 14px;

    padding:
        13px
        17px;

    font-size: 13px;

    opacity: 0;

    transform:
        translateY(20px);

    pointer-events: none;

    transition: .25s;

    z-index: 100;
}

.toast.show {

    opacity: 1;

    transform:
        translateY(0);
}


/* ============================================================
   MOBILE
   ============================================================ */

@media(max-width: 800px) {

    .sidebar {

        position: fixed;

        left: -290px;

        top: 0;

        bottom: 0;

        transition: .25s;

        box-shadow:
            10px 0 40px rgba(0,0,0,.5);
    }

    .sidebar.open {

        left: 0;
    }

    .mobile-menu {

        display: block;
    }

    .topbar {

        padding:
            0
            14px;
    }

    .content {

        padding: 20px 14px;
    }

    .hero {

        min-height:
            calc(100vh - 150px);
    }

    .bubble {

        max-width: 82vw;
    }

    .chat-page {

        height:
            calc(100vh - 106px);
    }
}


/* ============================================================
   SMALL PHONES
   ============================================================ */

@media(max-width: 450px) {

    .logo {

        padding-bottom: 15px;
    }

    .hero h1 {

        font-size: 32px;
    }

    .hero p {

        font-size: 13px;
    }

    .section-title {

        font-size: 25px;
    }

    .message-avatar {

        width: 32px;

        min-width: 32px;

        height: 32px;
    }

    .bubble {

        font-size: 13px;

        padding: 11px 13px;
    }

    .quick-button {

        font-size: 11px;
    }
}

</style>

</head>


<body>

<div class="app">


    <!-- =====================================================
         SIDEBAR
         ===================================================== -->

    <aside class="sidebar" id="sidebar">

        <div class="logo">

            <div class="logo-fire">
                🔥
            </div>

            <div class="logo-name">
                Companion AI
            </div>

        </div>


        <nav class="nav">

            <button
                class="nav-button active"
                data-page="chat"
            >
                <span class="nav-icon">💬</span>
                <span>Chat</span>
            </button>


            <button
                class="nav-button"
                data-page="codex"
            >
                <span class="nav-icon">💻</span>
                <span>Codex</span>
            </button>


            <button
                class="nav-button"
                data-page="image"
            >
                <span class="nav-icon">🖼️</span>
                <span>Generate Image</span>
            </button>


            <button
                class="nav-button"
                data-page="video"
            >
                <span class="nav-icon">🎬</span>
                <span>Generate Video</span>
            </button>


            <button
                class="nav-button"
                data-page="vibe"
            >
                <span class="nav-icon">✨</span>
                <span>Vibe</span>
            </button>


            <button
                class="nav-button"
                data-page="library"
            >
                <span class="nav-icon">📚</span>
                <span>Library</span>
            </button>


            <button
                class="nav-button"
                data-page="explore"
            >
                <span class="nav-icon">🌎</span>
                <span>Explore</span>
            </button>


            <button
                class="nav-button"
                data-page="settings"
            >
                <span class="nav-icon">⚙️</span>
                <span>Settings</span>
            </button>


            <button
                class="nav-button"
                id="newChatButton"
            >
                <span class="nav-icon">＋</span>
                <span>New Chat</span>
            </button>

        </nav>


        <div class="account">

            <div class="avatar">
                C
            </div>

            <div>

                <div class="account-name">
                    Companion User
                </div>

                <div class="account-status">
                    Free account
                </div>

            </div>

        </div>

    </aside>



    <!-- =====================================================
         MAIN
         ===================================================== -->

    <main class="main">


        <!-- TOP BAR -->

        <header class="topbar">

            <div style="display:flex;align-items:center;gap:12px;">

                <button
                    class="mobile-menu"
                    id="mobileMenu"
                >
                    ☰
                </button>

                <div class="top-title">

                    <span id="pageTitle">
                        Companion AI
                    </span>

                </div>

            </div>


            <div class="online">

                <span class="online-dot"></span>

                Online

            </div>

        </header>



        <!-- CONTENT -->

        <div class="content">


            <!-- =================================================
                 CHAT PAGE
                 ================================================= -->

            <section
                class="page active"
                id="page-chat"
            >

                <div class="chat-page">

                    <div class="chat-header">

                        <h2>
                            What can I help you with?
                        </h2>

                        <p>
                            Ask questions, code, create, explore,
                            or just have a conversation.
                        </p>

                    </div>


                    <div
                        class="messages"
                        id="messages"
                    >

                        <div class="message">

                            <div class="message-avatar">
                                🔥
                            </div>

                            <div class="bubble">
                                Hello! I'm Companion AI. What would you like to do?
                            </div>

                        </div>

                    </div>


                    <div class="composer-area">

                        <div class="quick-actions">

                            <button
                                class="quick-button"
                                data-prompt="Explain artificial intelligence in simple terms."
                            >
                                🤖 Explain AI
                            </button>

                            <button
                                class="quick-button"
                                data-prompt="Help me build a modern website."
                            >
                                🌐 Build a website
                            </button>

                            <button
                                class="quick-button"
                                data-prompt="Write a Python program that is useful and interesting."
                            >
                                🐍 Write Python
                            </button>

                            <button
                                class="quick-button"
                                data-prompt="Give me three creative project ideas."
                            >
                                💡 Give me ideas
                            </button>

                        </div>


                        <div class="composer">

                            <textarea
                                id="chatInput"
                                rows="1"
                                placeholder="Message Companion AI..."
                            ></textarea>

                            <button
                                class="send-button"
                                id="sendButton"
                            >
                                ➤
                            </button>

                        </div>


                        <div class="status" id="status">
                            Companion AI can make mistakes. Check important information.
                        </div>

                    </div>

                </div>

            </section>



            <!-- =================================================
                 CODEX
                 ================================================= -->

            <section
                class="page"
                id="page-codex"
            >

                <h1 class="section-title">
                    💻 Codex
                </h1>

                <p class="section-description">
                    Get help with programming, debugging,
                    websites, APIs, applications, and software.
                </p>


                <div class="grid">

                    <div
                        class="card"
                        data-codex-prompt="Create a responsive HTML and CSS website."
                    >

                        <div class="card-icon">
                            🌐
                        </div>

                        <h3>
                            Web Development
                        </h3>

                        <p>
                            Build responsive websites with HTML,
                            CSS, JavaScript, and Flask.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-codex-prompt="Write a useful Python application."
                    >

                        <div class="card-icon">
                            🐍
                        </div>

                        <h3>
                            Python
                        </h3>

                        <p>
                            Create Python programs and applications.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-codex-prompt="Help me debug this code and explain the problem."
                    >

                        <div class="card-icon">
                            🐛
                        </div>

                        <h3>
                            Debugging
                        </h3>

                        <p>
                            Find problems in your code and explain
                            how to fix them.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-codex-prompt="Explain how APIs work and show me an example."
                    >

                        <div class="card-icon">
                            🔌
                        </div>

                        <h3>
                            APIs
                        </h3>

                        <p>
                            Work with APIs, requests, JSON,
                            authentication, and web services.
                        </p>

                    </div>

                </div>

            </section>



            <!-- =================================================
                 IMAGE
                 ================================================= -->

            <section
                class="page"
                id="page-image"
            >

                <h1 class="section-title">
                    🖼️ Generate Image
                </h1>

                <p class="section-description">
                    Describe the image you want to create.
                </p>


                <div class="image-box">

                    <textarea
                        id="imagePrompt"
                        class="big-input"
                        placeholder="Example: A futuristic city at night with glowing neon buildings, cinematic lighting..."
                    ></textarea>


                    <button
                        class="primary-button"
                        id="generateImageButton"
                    >
                        Generate Image
                    </button>


                    <div
                        id="imageStatus"
                        style="
                            color:#777;
                            font-size:12px;
                            margin-top:12px;
                        "
                    ></div>


                    <img
                        id="generatedImage"
                        class="generated-image"
                        alt="Generated image"
                    >

                </div>

            </section>



            <!-- =================================================
                 VIDEO
                 ================================================= -->

            <section
                class="page"
                id="page-video"
            >

                <h1 class="section-title">
                    🎬 Generate Video
                </h1>

                <p class="section-description">
                    Describe your video idea and Companion AI
                    will create a detailed generation prompt.
                </p>


                <div class="image-box">

                    <textarea
                        id="videoPrompt"
                        class="big-input"
                        placeholder="Example: A futuristic sports car driving through a neon city during a rainstorm..."
                    ></textarea>


                    <button
                        class="primary-button"
                        id="generateVideoButton"
                    >
                        Create Video Prompt
                    </button>


                    <div
                        id="videoResult"
                        class="bubble"
                        style="
                            margin-top:20px;
                            display:none;
                            max-width:none;
                        "
                    ></div>

                </div>

            </section>



            <!-- =================================================
                 VIBE
                 ================================================= -->

            <section
                class="page"
                id="page-vibe"
            >

                <h1 class="section-title">
                    ✨ Vibe
                </h1>

                <p class="section-description">
                    A more relaxed and creative Companion AI experience.
                </p>


                <div class="grid">

                    <div
                        class="card"
                        data-vibe-prompt="Give me five creative ideas for a futuristic app."
                    >

                        <div class="card-icon">
                            🚀
                        </div>

                        <h3>
                            Creative Ideas
                        </h3>

                        <p>
                            Generate unusual and interesting ideas.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-vibe-prompt="Create an original futuristic character concept."
                    >

                        <div class="card-icon">
                            🧙
                        </div>

                        <h3>
                            Characters
                        </h3>

                        <p>
                            Create characters and concepts.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-vibe-prompt="Give me an original game concept with interesting gameplay."
                    >

                        <div class="card-icon">
                            🎮
                        </div>

                        <h3>
                            Game Ideas
                        </h3>

                        <p>
                            Explore game concepts and mechanics.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-vibe-prompt="Give me a creative idea for a futuristic AI project."
                    >

                        <div class="card-icon">
                            🤖
                        </div>

                        <h3>
                            AI Projects
                        </h3>

                        <p>
                            Brainstorm AI-powered projects.
                        </p>

                    </div>

                </div>

            </section>



            <!-- =================================================
                 LIBRARY
                 ================================================= -->

            <section
                class="page"
                id="page-library"
            >

                <h1 class="section-title">
                    📚 Library
                </h1>

                <p class="section-description">
                    Your saved conversations are stored in your browser.
                </p>


                <div
                    class="library-list"
                    id="libraryList"
                ></div>

            </section>



            <!-- =================================================
                 EXPLORE
                 ================================================= -->

            <section
                class="page"
                id="page-explore"
            >

                <h1 class="section-title">
                    🌎 Explore
                </h1>

                <p class="section-description">
                    Explore ideas and useful AI-powered workflows.
                </p>


                <div class="grid">

                    <div
                        class="card"
                        data-explore-prompt="Give me ten interesting technology project ideas."
                    >

                        <div class="card-icon">
                            🧪
                        </div>

                        <h3>
                            Technology
                        </h3>

                        <p>
                            Discover technology project ideas.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-explore-prompt="Give me five interesting AI application ideas."
                    >

                        <div class="card-icon">
                            🤖
                        </div>

                        <h3>
                            AI
                        </h3>

                        <p>
                            Discover ways AI can be used.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-explore-prompt="Give me five interesting game development project ideas."
                    >

                        <div class="card-icon">
                            🎮
                        </div>

                        <h3>
                            Games
                        </h3>

                        <p>
                            Explore game development concepts.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-explore-prompt="Give me creative ideas for a modern web application."
                    >

                        <div class="card-icon">
                            💡
                        </div>

                        <h3>
                            Apps
                        </h3>

                        <p>
                            Discover new application ideas.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-explore-prompt="Explain five emerging technologies in simple language."
                    >

                        <div class="card-icon">
                            ⚡
                        </div>

                        <h3>
                            Discover
                        </h3>

                        <p>
                            Explore interesting technologies.
                        </p>

                    </div>


                    <div
                        class="card"
                        data-explore-prompt="Give me ideas for a futuristic AI assistant."
                    >

                        <div class="card-icon">
                            🔥
                        </div>

                        <h3>
                            Build
                        </h3>

                        <p>
                            Turn ideas into projects.
                        </p>

                    </div>

                </div>

            </section>



            <!-- =================================================
                 SETTINGS
                 ================================================= -->

            <section
                class="page"
                id="page-settings"
            >

                <h1 class="section-title">
                    ⚙️ Settings
                </h1>

                <p class="section-description">
                    Customize your Companion AI experience.
                </p>


                <div class="setting">

                    <div>

                        <h3>
                            Fire Neon Theme
                        </h3>

                        <p>
                            Use the fire/neon interface.
                        </p>

                    </div>


                    <div
                        class="toggle on"
                        id="themeToggle"
                    >

                        <div class="toggle-circle"></div>

                    </div>

                </div>


                <div class="setting">

                    <div>

                        <h3>
                            Save Conversations
                        </h3>

                        <p>
                            Save chats locally in your browser.
                        </p>

                    </div>


                    <div
                        class="toggle on"
                        id="saveToggle"
                    >

                        <div class="toggle-circle"></div>

                    </div>

                </div>


                <div class="setting">

                    <div>

                        <h3>
                            Clear Library
                        </h3>

                        <p>
                            Delete all locally saved conversations.
                        </p>

                    </div>


                    <button
                        class="primary-button"
                        id="clearLibrary"
                    >
                        Clear
                    </button>

                </div>


                <div
                    class="setting"
                    style="display:block;"
                >

                    <h3>
                        About Companion AI
                    </h3>

                    <p style="margin-top:8px;line-height:1.6;">
                        Companion AI is a general-purpose AI interface
                        designed for conversation, coding, creativity,
                        image generation, video prompt creation,
                        and exploration.
                    </p>

                </div>

            </section>


        </div>

    </main>

</div>


<div
    class="toast"
    id="toast"
>
    Saved
</div>


<script>


// ============================================================
// STATE
// ============================================================

let currentMode = "chat";

let currentMessages = [];

let saveConversations = true;


// ============================================================
// ELEMENTS
// ============================================================

const sidebar =
    document.getElementById("sidebar");

const mobileMenu =
    document.getElementById("mobileMenu");

const pageTitle =
    document.getElementById("pageTitle");

const messages =
    document.getElementById("messages");

const chatInput =
    document.getElementById("chatInput");

const sendButton =
    document.getElementById("sendButton");

const status =
    document.getElementById("status");


// ============================================================
// PAGE TITLES
// ============================================================

const titles = {

    chat: "Companion AI",

    codex: "Codex",

    image: "Generate Image",

    video: "Generate Video",

    vibe: "Vibe",

    library: "Library",

    explore: "Explore",

    settings: "Settings"

};


// ============================================================
// NAVIGATION
// ============================================================

function openPage(page) {

    currentMode = page;

    document
        .querySelectorAll(".page")
        .forEach(function(el) {

            el.classList.remove("active");

        });


    const target =
        document.getElementById(
            "page-" + page
        );

    if (target) {

        target.classList.add("active");

    }


    document
        .querySelectorAll(".nav-button[data-page]")
        .forEach(function(button) {

            button.classList.remove("active");

            if (
                button.dataset.page === page
            ) {

                button.classList.add("active");

            }

        });


    pageTitle.textContent =
        titles[page] || "Companion AI";


    sidebar.classList.remove("open");


    if (page === "library") {

        renderLibrary();

    }

}


// ============================================================
// NAV BUTTONS
// ============================================================

document
    .querySelectorAll(".nav-button[data-page]")
    .forEach(function(button) {

        button.addEventListener(
            "click",
            function() {

                openPage(
                    button.dataset.page
                );

            }
        );

    });


// ============================================================
// MOBILE MENU
// ============================================================

mobileMenu.addEventListener(
    "click",
    function() {

        sidebar.classList.toggle(
            "open"
        );

    }
);


// ============================================================
// TOAST
// ============================================================

function toast(message) {

    const element =
        document.getElementById("toast");

    element.textContent = message;

    element.classList.add("show");

    setTimeout(
        function() {

            element.classList.remove(
                "show"
            );

        },
        2200
    );

}


// ============================================================
// ADD MESSAGE
// ============================================================

function addMessage(
    text,
    type = "assistant"
) {

    const message =
        document.createElement("div");

    message.className =
        "message " + type;


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        type === "user"
            ? "U"
            : "🔥";


    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";

    bubble.textContent =
        text;


    message.appendChild(
        avatar
    );

    message.appendChild(
        bubble
    );

    messages.appendChild(
        message
    );


    messages.scrollTop =
        messages.scrollHeight;


    currentMessages.push({

        role:
            type === "user"
                ? "user"
                : "assistant",

        content:
            text

    });

}


// ============================================================
// SEND CHAT
// ============================================================

async function sendMessage(
    customText = null,
    mode = "chat"
) {

    let message =
        customText !== null
            ? customText
            : chatInput.value.trim();


    if (!message) {

        return;

    }


    openPage("chat");


    addMessage(
        message,
        "user"
    );


    if (
        customText === null
    ) {

        chatInput.value = "";

    }


    chatInput.style.height =
        "42px";


    sendButton.disabled =
        true;


    status.textContent =
        "Companion AI is thinking...";


    const loading =
        document.createElement("div");

    loading.className =
        "message";

    loading.id =
        "loadingMessage";


    loading.innerHTML = `
        <div class="message-avatar">🔥</div>
        <div class="bubble">Thinking...</div>
    `;


    messages.appendChild(
        loading
    );


    messages.scrollTop =
        messages.scrollHeight;


    try {

        const response =
            await fetch(
                "/ask",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        message:
                            message,

                        mode:
                            mode

                    })

                }
            );


        const data =
            await response.json();


        const loader =
            document.getElementById(
                "loadingMessage"
            );


        if (loader) {

            loader.remove();

        }


        if (
            data.type === "image"
        ) {

            addMessage(
                data.text,
                "assistant"
            );

            const image =
                document.createElement(
                    "img"
                );

            image.src =
                data.image;

            image.style.width =
                "min(600px, 80vw)";

            image.style.borderRadius =
                "18px";

            image.style.marginTop =
                "10px";

            messages.appendChild(
                image
            );

        } else {

            addMessage(
                data.text,
                "assistant"
            );

        }


        status.textContent =
            "Ready";


        if (
            saveConversations
        ) {

            saveCurrentConversation();

        }

    }
    catch (error) {

        const loader =
            document.getElementById(
                "loadingMessage"
            );


        if (loader) {

            loader.remove();

        }


        addMessage(
            "Something went wrong while connecting to the AI service.",
            "assistant"
        );


        status.textContent =
            "Connection error";

    }


    sendButton.disabled =
        false;

}


// ============================================================
// SEND BUTTON
// ============================================================

sendButton.addEventListener(
    "click",
    function() {

        sendMessage();

    }
);


// ============================================================
// ENTER TO SEND
// ============================================================

chatInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


// ============================================================
// TEXTAREA AUTO RESIZE
// ============================================================

chatInput.addEventListener(
    "input",
    function() {

        chatInput.style.height =
            "42px";

        chatInput.style.height =
            Math.min(
                chatInput.scrollHeight,
                160
            ) + "px";

    }
);


// ============================================================
// QUICK BUTTONS
// ============================================================

document
    .querySelectorAll(".quick-button")
    .forEach(function(button) {

        button.addEventListener(
            "click",
            function() {

                sendMessage(
                    button.dataset.prompt,
                    "chat"
                );

            }
        );

    });


// ============================================================
// CODEX CARDS
// ============================================================

document
    .querySelectorAll("[data-codex-prompt]")
    .forEach(function(card) {

        card.addEventListener(
            "click",
            function() {

                sendMessage(
                    card.dataset.codexPrompt,
                    "codex"
                );

            }
        );

    });


// ============================================================
// VIBE CARDS
// ============================================================

document
    .querySelectorAll("[data-vibe-prompt]")
    .forEach(function(card) {

        card.addEventListener(
            "click",
            function() {

                sendMessage(
                    card.dataset.vibePrompt,
                    "vibe"
                );

            }
        );

    });


// ============================================================
// EXPLORE CARDS
// ============================================================

document
    .querySelectorAll("[data-explore-prompt]")
    .forEach(function(card) {

        card.addEventListener(
            "click",
            function() {

                sendMessage(
                    card.dataset.explorePrompt,
                    "explore"
                );

            }
        );

    });


// ============================================================
// IMAGE GENERATION
// ============================================================

document
    .getElementById("generateImageButton")
    .addEventListener(
        "click",
        async function() {

            const prompt =
                document
                    .getElementById(
                        "imagePrompt"
                    )
                    .value
                    .trim();


            if (!prompt) {

                toast(
                    "Describe the image first."
                );

                return;

            }


            const status =
                document
                    .getElementById(
                        "imageStatus"
                    );

            const image =
                document
                    .getElementById(
                        "generatedImage"
                    );


            status.textContent =
                "Generating image...";


            image.style.display =
                "none";


            try {

                const response =
                    await fetch(
                        "/ask",
                        {

                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    message:
                                        prompt,

                                    mode:
                                        "image"

                                })

                        }
                    );


                const data =
                    await response.json();


                if (
                    data.image
                ) {

                    image.src =
                        data.image;

                    image.onload =
                        function() {

                            image.style.display =
                                "block";

                        };


                    status.textContent =
                        "Image generated.";

                }

            }
            catch (error) {

                status.textContent =
                    "Image generation failed.";

            }

        }
    );


// ============================================================
// VIDEO GENERATION
// ============================================================

document
    .getElementById("generateVideoButton")
    .addEventListener(
        "click",
        async function() {

            const prompt =
                document
                    .getElementById(
                        "videoPrompt"
                    )
                    .value
                    .trim();


            if (!prompt) {

                toast(
                    "Describe your video first."
                );

                return;

            }


            const result =
                document
                    .getElementById(
                        "videoResult"
                    );


            result.style.display =
                "block";

            result.textContent =
                "Creating video prompt...";


            try {

                const response =
                    await fetch(
                        "/ask",
                        {

                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    message:
                                        prompt,

                                    mode:
                                        "video"

                                })

                        }
                    );


                const data =
                    await response.json();


                result.textContent =
                    data.text;


            }
            catch (error) {

                result.textContent =
                    "Unable to create the video prompt.";

            }

        }
    );


// ============================================================
// LIBRARY STORAGE
// ============================================================

function getLibrary() {

    try {

        return JSON.parse(
            localStorage.getItem(
                "companion_library"
            ) || "[]"
        );

    }
    catch (error) {

        return [];

    }

}


function saveLibrary(library) {

    localStorage.setItem(
        "companion_library",
        JSON.stringify(library)
    );

}


// ============================================================
// SAVE CURRENT CONVERSATION
// ============================================================

function saveCurrentConversation() {

    if (
        currentMessages.length < 2
    ) {

        return;

    }


    const library =
        getLibrary();


    const firstUser =
        currentMessages.find(
            function(item) {

                return item.role === "user";

            }
        );


    const title =
        firstUser
            ? firstUser.content.substring(
                0,
                60
            )
            : "New Conversation";


    const conversation = {

        id:
            Date.now(),

        title:
            title,

        date:
            new Date().toLocaleString(),

        messages:
            currentMessages

    };


    library.unshift(
        conversation
    );


    // Keep the library from growing forever
    const limited =
        library.slice(
            0,
            30
        );


    saveLibrary(
        limited
    );

}


// ============================================================
// RENDER LIBRARY
// ============================================================

function renderLibrary() {

    const container =
        document.getElementById(
            "libraryList"
        );


    const library =
        getLibrary();


    container.innerHTML =
        "";


    if (
        library.length === 0
    ) {

        container.innerHTML = `
            <div class="empty">
                No conversations saved yet.
                Start chatting and your conversations
                will appear here.
            </div>
        `;

        return;

    }


    library.forEach(
        function(item) {

            const element =
                document.createElement(
                    "div"
                );


            element.className =
                "library-item";


            element.innerHTML = `
                <div class="library-title">
                    ${escapeHtml(item.title)}
                </div>

                <div class="library-date">
                    ${escapeHtml(item.date)}
                </div>
            `;


            element.addEventListener(
                "click",
                function() {

                    loadConversation(
                        item
                    );

                }
            );


            container.appendChild(
                element
            );

        }
    );

}


// ============================================================
// LOAD CONVERSATION
// ============================================================

function loadConversation(
    conversation
) {

    openPage(
        "chat"
    );


    messages.innerHTML =
        "";


    currentMessages = [];


    conversation.messages.forEach(
        function(item) {

            addMessage(
                item.content,
                item.role === "user"
                    ? "user"
                    : "assistant"
            );

        }
    );


    toast(
        "Conversation opened"
    );

}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        text;

    return div.innerHTML;

}


// ============================================================
// NEW CHAT
// ============================================================

document
    .getElementById(
        "newChatButton"
    )
    .addEventListener(
        "click",
        function() {

            if (
                currentMessages.length >= 2 &&
                saveConversations
            ) {

                saveCurrentConversation();

            }


            currentMessages =
                [];


            messages.innerHTML = `

                <div class="message">

                    <div class="message-avatar">
                        🔥
                    </div>

                    <div class="bubble">
                        Hello! I'm Companion AI. What would you like to do?
                    </div>

                </div>

            `;


            currentMessages.push({

                role:
                    "assistant",

                content:
                    "Hello! I'm Companion AI. What would you like to do?"

            });


            chatInput.value =
                "";

            status.textContent =
                "Ready";


            openPage(
                "chat"
            );


            toast(
                "New chat started"
            );

        }
    );


// ============================================================
// SETTINGS - SAVE TOGGLE
// ============================================================

document
    .getElementById(
        "saveToggle"
    )
    .addEventListener(
        "click",
        function() {

            this.classList.toggle(
                "on"
            );


            saveConversations =
                this.classList.contains(
                    "on"
                );


            toast(
                saveConversations
                    ? "Conversation saving enabled"
                    : "Conversation saving disabled"
            );

        }
    );


// ============================================================
// SETTINGS - THEME TOGGLE
// ============================================================

document
    .getElementById(
        "themeToggle"
    )
    .addEventListener(
        "click",
        function() {

            this.classList.toggle(
                "on"
            );


            document.body.classList.toggle(
                "plain-theme"
            );

        }
    );


// ============================================================
// CLEAR LIBRARY
// ============================================================

document
    .getElementById(
        "clearLibrary"
    )
    .addEventListener(
        "click",
        function() {

            localStorage.removeItem(
                "companion_library"
            );


            renderLibrary();


            toast(
                "Library cleared"
            );

        }
    );


// ============================================================
// INITIALIZATION
// ============================================================

currentMessages.push({

    role:
        "assistant",

    content:
        "Hello! I'm Companion AI. What would you like to do?"

});


renderLibrary();


</script>

</body>

</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():

    return render_template_string(UI)


@app.route("/ask", methods=["POST"])
def ask():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        message = str(
            data.get(
                "message",
                ""
            )
        ).strip()

        mode = str(
            data.get(
                "mode",
                "chat"
            )
        ).lower()


        if not message:

            return jsonify({
                "type": "text",
                "text": "Please enter a message."
            })


        allowed_modes = {
            "chat",
            "codex",
            "image",
            "video",
            "vibe",
            "explore"
        }


        if mode not in allowed_modes:

            mode = "chat"


        result =
            smart(
                message,
                mode
            )


        return jsonify(
            result
        )


    except Exception as error:

        print(
            "ERROR:",
            error
        )

        return jsonify({

            "type":
                "text",

            "text":
                "An unexpected server error occurred."

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🔥 COMPANION AI")
    print("=" * 60)
    print("General AI interface")
    print()
    print("Open this address in your browser:")
    print("http://127.0.0.1:5000")
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )