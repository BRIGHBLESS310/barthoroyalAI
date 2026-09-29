from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os

app = Flask(__name__)

def get_answer(q, mode="learn"):
    mode_instructions = {
        "learn": "You are Companion AI, a friendly Nigerian JSS2 tutor. Explain simply.",
        "codex": "You are Codex, a concise expert programming assistant. Help debug, explain, and write code clearly.",
        "vibe": "You are Companion AI in Vibe mode: warm, relaxed, creative, and conversational.",
        "video": "You create detailed, ready-to-use video generation prompts. Return a vivid prompt with subject, action, setting, camera movement, lighting, and style. Do not claim to render a video.",
    }
    instruction = mode_instructions.get(mode, mode_instructions["learn"])
    # BRAIN 1: Pollinations OpenAI format (strongest free)
    try:
        url = "https://gen.pollinations.ai/v1/chat/completions"
        data = {
            "model": "openai",
            "messages": [{"role": "user", "content": f"{instruction}\n\nUser request: {q}"}],
            "max_tokens": 800
        }
        r = requests.post(url, json=data, timeout=25)
        if r.status_code == 200:
            j = r.json()
            ans = j['choices'][0]['message']['content']
            if len(ans) > 10:
                return ans
    except Exception as e:
        print("Brain1 fail:", e)

    # BRAIN 2: Simple pollinations GET
    try:
        url2 = f"https://text.pollinations.ai/{urllib.parse.quote(q)}"
        r2 = requests.get(url2, timeout=15)
        if r2.status_code == 200 and len(r2.text) > 10:
            return r2.text
    except:
        pass

    # BRAIN 3: Wikipedia backup
    try:
        wurl = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(q)}"
        rw = requests.get(wurl, timeout=10)
        if rw.status_code == 200:
            return rw.json().get('extract', None)
    except:
        pass

    # BRAIN 4: Local Ollama backup
    try:
        ollama_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
        ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
        ro = requests.post(
            ollama_url,
            json={
                "model": ollama_model,
                "messages": [
                    {"role": "system", "content": "You are Companion AI, a friendly Nigerian JSS2 tutor. Explain clearly and simply."},
                    {"role": "user", "content": q},
                ],
                "stream": False,
            },
            timeout=90,
        )
        if ro.status_code == 200:
            answer = ro.json().get("message", {}).get("content", "").strip()
            if len(answer) > 10:
                return answer
    except Exception as e:
        print("Ollama backup fail:", e)

    return None

def smart(q, generate_image=False, mode="learn"):
    if not q:
        return {"text": "Ask me!", "image": None}
    if generate_image or any(x in q.lower() for x in ["image", "draw", "picture"]):
        img = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(q)}?nologo=true&width=1024&height=1024"
        return {"text": f"Image: {q}", "image": img}

    ans = get_answer(q, mode)
    if ans:
        return {"text": ans, "image": None}

    # If all fail, give local answer for common questions
    low = q.lower()
    if "computer" in low:
        return {"text": """**What is a Computer for JSS2?**

A Computer is an electronic machine that can accept data, process data, store data and give out information.

**Types of Computer:**
1. Super Computer - very fast, for weather
2. Mainframe - big companies
3. Mini Computer - medium
4. Micro Computer - Desktop, Laptop, Phone

**Uses of Computer:**
1. In Schools - for teaching and learning
2. In Banks - to keep money records
3. In Hospitals - to check patients
4. For Communication - WhatsApp, Facebook
5. For Games and Entertainment
6. For Business - typing and calculation

**Parts of Computer:**
- Hardware: Keyboard, Mouse, Monitor
- Software: Windows, Apps

Computer makes work faster and easier!""", "image": None}

    return {"text": f"I dey try connect to free brain for '{q}'. Please wait 10 secs and try again! Network slow small.", "image": None}

UI = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="theme-color" content="#100b0a">
    <title>Companion AI |</title>
    <link rel="preconnect" href="https://wikipedia.com">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        :root{color-scheme:dark;--bg:#100b0a;--panel:#1b1110;--line:#39211c;--text:#fff4ec;--muted:#b89b8d;--fire:#ff713e;--gold:#ffc35c;--pink:#ff4f76}
        *{box-sizing:border-box}
        html{scroll-behavior:smooth}
        body{margin:0;min-height:100vh;background-color:var(--bg);background-image:linear-gradient(125deg,#40160c66,transparent 48%),linear-gradient(305deg,#3b101c55,transparent 50%),repeating-linear-gradient(125deg,#ffffff04 0,#ffffff04 1px,transparent 1px,transparent 58px);color:var(--text);font-family:'DM Sans',sans-serif}
        a{color:inherit;text-decoration:none}
        .topbar{height:72px;border-bottom:1px solid #ffffff12;background:#100b0acc;backdrop-filter:blur(16px);position:sticky;top:0;z-index:5}
        .nav{height:100%;max-width:1120px;padding:0 24px;margin:auto;display:flex;align-items:center;justify-content:space-between}
        .brand{display:flex;align-items:center;gap:11px;font:700 18px 'Space Grotesk',sans-serif;letter-spacing:0}
        .brand-mark{width:34px;height:34px;display:grid;place-items:center;border-radius:10px;color:#1b100b;background:linear-gradient(140deg,var(--gold),var(--fire) 62%,var(--pink));box-shadow:0 0 22px #ff633b55;font-weight:700}
        .brand small{display:block;margin-top:1px;color:var(--muted);font:500 10px 'DM Sans',sans-serif;letter-spacing:1.2px;text-transform:uppercase}
        .nav-links{display:flex;align-items:center;gap:4px;overflow-x:auto;scrollbar-width:none}
        .nav-links::-webkit-scrollbar{display:none}
        .nav-links button{flex:0 0 auto;padding:9px 11px;border:0;background:transparent;color:#c9b2a6;font:500 12px 'DM Sans',sans-serif;border-radius:8px;cursor:pointer;transition:color .2s,background .2s}
        .nav-links button:hover,.nav-links button.active{background:#ff713e16;color:var(--gold)}
        .nav-links button.new-chat{color:#24100b;background:linear-gradient(110deg,var(--gold),var(--fire));font-weight:700}
        .nav-status{display:flex;align-items:center;gap:8px;color:#d9c3b5;font-size:12px}
        .status-dot{width:8px;height:8px;border-radius:50%;background:#a8ed91;box-shadow:0 0 10px #a8ed91}
        main{max-width:900px;margin:0 auto;padding:44px 24px 30px;animation:arrive .55s ease-out both}
        @keyframes arrive{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        .eyebrow{color:var(--fire);font-size:11px;font-weight:700;letter-spacing:1.8px;text-transform:uppercase}
        h1{font:600 40px/1.12 'Space Grotesk',sans-serif;letter-spacing:0;margin:10px 0 8px}
        .intro{margin:0;color:var(--muted);font-size:14px}
        .subjects{margin:27px 0 16px}
        .section-label{margin:0 0 10px;color:#c9ada0;font-size:12px;font-weight:600}
        .subject-list{display:flex;flex-wrap:wrap;gap:9px}
        .subject{padding:9px 13px;border:1px solid var(--line);border-radius:8px;background:#1a100e;color:#efdbce;font:500 12px 'DM Sans',sans-serif;cursor:pointer;transition:border-color .18s,box-shadow .18s,transform .18s}
        .subject:hover{border-color:var(--fire);box-shadow:0 0 16px #ff713e22;transform:translateY(-1px)}
        .chat-panel{overflow:hidden;border:1px solid #583025;border-radius:12px;background:linear-gradient(145deg,#211411ed,#160f0eeb);box-shadow:0 20px 70px #0008,0 0 36px #ff54200b}
        .chat-head{min-height:56px;padding:0 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ffffff10}
        .chat-heading{font:600 14px 'Space Grotesk',sans-serif}
        .chat-caption{color:#c7a99a;font-size:11px}
        #chat{height:min(48vh,430px);min-height:280px;overflow:auto;padding:15px 18px;scroll-behavior:smooth}
        .message{width:fit-content;max-width:min(84%,640px);margin:9px 0;padding:12px 14px;border:1px solid #ffffff12;border-radius:10px;background:#281b18;color:#f5e6dd;white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;line-height:1.65}
        .message.user{margin-left:auto;border-color:#ff713e5c;background:#512518;color:#fff4ec}
        .message.loading{color:var(--gold)}
        .message img{display:block;width:min(100%,440px);margin-top:10px;border-radius:8px}
        .composer{padding:13px;display:flex;gap:10px;border-top:1px solid #ffffff10;background:#130d0c}
        #q{width:100%;min-width:0;padding:12px 14px;border:1px solid #51342c;border-radius:8px;outline:none;background:#1a1210;color:var(--text);font:14px 'DM Sans',sans-serif}
        #q:focus{border-color:var(--fire);box-shadow:0 0 0 3px #ff713e1c}
        #q::placeholder{color:#987f73}
        #send{min-width:86px;padding:0 16px;border:0;border-radius:8px;background:linear-gradient(110deg,var(--gold),var(--fire) 68%,var(--pink));color:#24100b;font:700 13px 'DM Sans',sans-serif;cursor:pointer;transition:filter .2s,transform .2s}
        #send:hover{filter:brightness(1.12);transform:translateY(-1px)}
        #send:disabled{opacity:.55;cursor:wait;transform:none}
        .about{padding:17px 0 0;color:#a88f82;font-size:11px}
        .library-view{display:none;margin-top:25px;border-top:1px solid #ffffff18;padding-top:18px}
        .library-view.open{display:block}
        .library-item{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:13px 14px;margin:8px 0;border:1px solid var(--line);border-radius:8px;background:#1a100e;color:var(--text);text-align:left;cursor:pointer}
        .library-item:hover{border-color:var(--fire)}
        .library-item small{color:var(--muted)}
        .empty-library{color:var(--muted);font-size:13px}
        @media(max-width:850px){.nav{gap:14px}.brand{flex:0 0 auto}.nav-links{flex:1;justify-content:flex-start}.nav-status{display:none}}
        @media(max-width:600px){.topbar{height:64px}.nav{padding:0 12px;gap:8px}.brand{font-size:15px;gap:7px}.brand-mark{width:30px;height:30px}.brand small{font-size:9px}.nav-links{gap:0}.nav-links button{padding:9px 8px;font-size:11px}main{padding:32px 15px 22px}h1{font-size:32px}.subjects{margin-top:22px}#chat{height:44vh;min-height:250px;padding:12px}.message{max-width:92%}.composer{padding:10px}.about{padding-bottom:10px}}
    </style>
</head>
<body>
    <header class="topbar" id="top">
        <nav class="nav" aria-label="Main navigation">
            <a class="brand" href="#top"><span class="brand-mark">C</span><span>Companion AI<small>cAI School</small></span></a>
            <div class="nav-links" aria-label="Workspace tools">
                <button class="new-chat" type="button" data-action="new-chat">+ New chat</button>
                <button type="button" data-mode="codex">Codex</button>
  ke              <button type="button" data-mode="image">Generate image</button>
                <button type="button" data-mode="video">Generate video</button>
                <button type="button" data-action="library">Library</button>
                <button type="button" data-mode="vibe">Vibe</button>
                <button class="active" type="button" data-mode="learn">Learn</button>
                <button type="button" data-action="explore">Explore</button>
            </div>
            <div class="nav-status"><span class="status-dot"></span>Ready to help</div>
        </nav>
    </header>
    <main id="learn">
        <section class="subjects" id="subjects" aria-labelledby="subject-label">
        </section>
        <section class="library-view" id="library-view" aria-label="Saved chats">
            <h2 class="section-label">Your library</h2>
            <div id="library-list"></div>
        </section>
        <section class="chat-panel" aria-label="Study chat">
            <div class="chat-head"><span class="chat-heading" id="chat-heading">Study chat</span><span class="chat-caption" id="chat-caption">JSS2 learning assistant</span></div>
            <div id="chat" aria-live="polite"><div class="message">Ready when you are. Ask me anything about your studies.</div></div>
            <form class="composer" id="composer">
                <input id="q" autocomplete="off" placeholder="Ask anything..." aria-label="Your question">
                <button id="send" type="submit">Ask</button>
            </form>
        </section>
        <footer class="about" id="about">Companion AI <span aria-hidden="true">&middot;</span> can make mistake check for important information</footer>
    </main>
    <script>
        const input = document.getElementById('q');
        const chat = document.getElementById('chat');
        const sendButton = document.getElementById('send');
        const modeLabel = document.getElementById('mode-label');
        const pageTitle = document.getElementById('page-title');
        const pageIntro = document.getElementById('page-intro');
        const chatHeading = document.getElementById('chat-heading');
        const chatCaption = document.getElementById('chat-caption');
        const libraryView = document.getElementById('library-view');
        let currentMode = 'learn';
        let transcript = [{kind: '', text: 'Ready when you are. .'}];

        const modeCopy = {
            learn: ['Your study space', 'What are we learning today?', 'Ask a question or pick a subject to get started.', 'Study chat', 'JSS2 learning assistant'],
            codex: ['Code workspace', 'Let’s build something.', 'Ask for code, an explanation, or help debugging.', 'Codex', 'Programming assistant'],
            image: ['Image studio', 'What should we imagine?', 'Describe an image and Companion will create it.', 'Image generation', 'Image studio'],
            video: ['Video studio', 'Set a scene in motion.', 'Describe the clip you want and get a detailed generation prompt.', 'Video prompt builder', 'Creates prompts, not video files'],
            vibe: ['Vibe mode', 'What’s on your mind?','funny','coder', 'Bring a question, an idea, or just start a conversation.', 'Vibe chat', 'Relaxed conversation']
        };

        function saveCurrentChat() {
            if (!transcript.some(message => message.kind === 'user')) return;
            try {
                const library = JSON.parse(localStorage.getItem('companion-library') || '[]');
                const title = transcript.find(message => message.kind === 'user')?.text || 'New chat';
                const entry = {id: Date.now(), title: title.slice(0, 72), updated: new Date().toLocaleString(), transcript};
                localStorage.setItem('companion-library', JSON.stringify([entry, ...library].slice(0, 30)));
            } catch (error) {
                console.warn('Could not save chat locally.', error);
            }
        }

        function renderTranscript(messages) {
            chat.replaceChildren();
            transcript = messages;
            messages.forEach(message => {
                const node = addMessage(message.text, message.kind, false);
                if (message.image) {
                    const image = document.createElement('img');
                    image.src = message.image;
                    image.alt = message.text;
                    node.appendChild(image);
                }
            });
        }

        function addMessage(text, kind, record = true) {
            const message = document.createElement('div');
            message.className = `message ${kind}`.trim();
            message.textContent = text;
            chat.appendChild(message);
            chat.scrollTop = chat.scrollHeight;
            if (record && kind !== 'loading') transcript.push({text, kind});
            return message;
        }

        function renderLibrary() {
            const list = document.getElementById('library-list');
            list.replaceChildren();
            let entries = [];
            try { entries = JSON.parse(localStorage.getItem('companion-library') || '[]'); } catch (error) {}
            if (!entries.length) {
                list.innerHTML = '<p class="empty-library">Saved conversations will appear here.</p>';
                return;
            }
            entries.forEach(entry => {
                const button = document.createElement('button');
                button.className = 'library-item';
                button.type = 'button';
                const title = document.createElement('span');
                title.textContent = entry.title;
                const date = document.createElement('small');
                date.textContent = entry.updated;
                button.append(title, date);
                button.addEventListener('click', () => {
                    renderTranscript(entry.transcript);
                    libraryView.classList.remove('open');
                    document.querySelector('.chat-panel').hidden = false;
                });
                list.appendChild(button);
            });
        }

        function setMode(mode) {
            currentMode = mode;
            const copy = modeCopy[mode];
            document.querySelectorAll('[data-mode]').forEach(button => button.classList.toggle('active', button.dataset.mode === mode));
            libraryView.classList.remove('open');
            document.querySelector('.chat-panel').hidden = false;
            document.querySelector('.subjects').hidden = mode !== 'learn';
            [modeLabel.textContent, pageTitle.textContent, pageIntro.textContent, chatHeading.textContent, chatCaption.textContent] = copy;
            input.placeholder = mode === 'image' ? 'Describe the image you want...' : mode === 'video' ? 'Describe the video scene...' : 'Ask anything...';
            sendButton.textContent = mode === 'image' ? 'Create' : mode === 'video' ? 'Prompt' : 'Ask';
            input.focus();
        }

        async function ask(question) {
            const text = question.trim();
            if (!text || sendButton.disabled) return;
            addMessage(text, 'user');
            input.value = '';
            sendButton.disabled = true;
            const loading = addMessage('got it...', 'loading');
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({q: text, mode: currentMode, generate_image: currentMode === 'image'})
                });
                if (!response.ok) throw new Error('Request failed');
                const result = await response.json();
                loading.remove();
                const answer = addMessage(result.a || 'I could not find an answer. Please try again.', '');
                const lastMessage = transcript[transcript.length - 1];
                if (result.image) {
                    const image = document.createElement('img');
                    image.src = result.image;
                    image.alt = text;
                    answer.appendChild(image);
                    lastMessage.image = result.image;
                }
                saveCurrentChat();
            } catch (error) {
                loading.textContent = 'something went wrong with our ends pls try again later.';
            } finally {
                sendButton.disabled = false;
                input.focus();
            }
        }

        document.getElementById('composer').addEventListener('submit', event => {
            event.preventDefault();
            ask(input.value);
        });
        document.querySelectorAll('[data-prompt]').forEach(button => {
            button.addEventListener('click', () => ask(button.dataset.prompt));
        });
        document.querySelectorAll('[data-mode]').forEach(button => {
            button.addEventListener('click', () => setMode(button.dataset.mode));
        });
        document.querySelector('[data-action="new-chat"]').addEventListener('click', () => {
            saveCurrentChat();
            setMode('learn');
            transcript = [{kind: '',  text: 'Ready when you are. .'}];
            renderTranscript(transcript);
            input.value = '';
        });
        document.querySelector('[data-action="library"]').addEventListener('click', () => {
            renderLibrary();
            libraryView.classList.add('open');
            document.querySelector('.chat-panel').hidden = true;
            document.querySelector('.subjects').hidden = true;
            pageTitle.textContent = 'Your conversations';
            pageIntro.textContent = 'Pick up where you left off.';
            modeLabel.textContent = 'Library';
        });
        document.querySelector('[data-action="explore"]').addEventListener('click', () => {
            setMode('learn');
            document.querySelector('.subjects').scrollIntoView({behavior: 'smooth', block: 'center'});
        });
    </script>
</body>
</html>"""

@app.route('/')
def h(): return render_template_string(UI)
@app.route('/logo.png')
def l():
    try: return send_from_directory('.', 'logo.png')
    except: return "",404
@app.route('/ask', methods=['POST'])
def ask():
    payload = request.get_json(silent=True) or {}
    q = payload.get('q', '')
    mode = payload.get('mode', 'learn')
    res = smart(q, generate_image=payload.get('generate_image', False), mode=mode)
    return jsonify({"a": res["text"], "image": res["image"]})

if __name__ == '__main__': app.run()