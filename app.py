from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os, re, math
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0"}

def solve_math(q):
    try:
        low = q.lower()
        # Extract math expression
        # Check if it's a calculation
        if any(k in low for k in ["calculate", "solve", "what is", "evaluate"]):
            # Try to find equation like 2+2, 2*5, 10/2 etc
            expr = re.sub(r'[^0-9+\-*/().%x= ]', '', q)
            expr = expr.replace('x', '*').replace('X', '*')
            if '=' in expr:
                # Simple equation like 2x+5=15 -> handle linear
                if 'calculate' in low or 'solve' in low:
                    # Try eval for simple
                    left = expr.split('=')[0].strip()
                    right = expr.split('=')[1].strip()
                    # Very simple linear solver
                    return f"📐 Math Solver:\n\nEquation: {q}\n\nLet me solve step-by-step...\n\nIf {expr}, then:\n{left} = {right}\n\nUse calculator for final value."
            # Simple arithmetic
            clean_expr = re.findall(r'[\d+\-*/().% ]+', q)
            if clean_expr:
                for e in clean_expr:
                    e = e.strip()
                    if len(e) > 1 and any(op in e for op in ['+','-','*','/']):
                        try:
                            # Safe eval
                            result = eval(e, {"__builtins__": None}, {"math": math})
                            return f"📐 Mathematics Answer:\n\n{e} = {result}\n\nSolved successfully!"
                        except:
                            continue
        return None
    except:
        return None

def google_search(q):
    try:
        # DuckDuckGo Instant Answer
        r = requests.get(f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1&skip_disambig=1", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = r.json()
        if data.get('AbstractText'):
            return f"{data['AbstractText']}\n\n📚 Source: DuckDuckGo - {data.get('AbstractURL','')}"
        if data.get('RelatedTopics'):
            for topic in data['RelatedTopics'][:3]:
                if isinstance(topic, dict) and topic.get('Text'):
                    if len(topic.get('Text','')) > 50:
                        return f"{topic['Text'][:800]}\n\n📚 Source: DuckDuckGo"
        # Wikipedia search fallback
        wiki_search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json"
        r2 = requests.get(wiki_search_url, headers=HEADERS, timeout=8)
        d2 = r2.json()
        if d2.get('query',{}).get('search'):
            snippet = d2['query']['search'][0]['snippet']
            title = d2['query']['search'][0]['title']
            clean = BeautifulSoup(snippet, 'html.parser').get_text()
            return f"📚 {title}:\n\n{clean[:800]}\n\nSource: Wikipedia"
        return None
    except Exception as e:
        return None

def wiki_search(q):
    try:
        query = q.replace("who is","").replace("what is","").replace("tell me about","").replace("explain","").strip() or q
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code==200:
            data=r.json()
            text = data.get('extract','')
            img = data.get('thumbnail',{}).get('source') or data.get('originalimage',{}).get('source')
            if text:
                return {"text": text, "image": img}
        return None
    except:
        return None

def smart_answer(q):
    low = q.lower().strip()

    # 1. IMAGE GENERATION
    is_image = any(k in low for k in ["generate image", "create image", "make image", "draw", "imagine", "picture of", "image of"])
    if is_image:
        prompt = q
        for k in ["generate image of", "generate image", "create image", "make image", "draw", "image of", "picture of", "imagine"]:
            if k in low:
                prompt = q.lower().split(k, 1)[-1].strip()
                break
        if len(prompt) < 3: prompt = q
        safe_prompt = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed={abs(hash(q))%100000}&nologo=true"
        return {"text": f"🎨 Created: {prompt}", "image": img_url}

    # 2. MATHEMATICS
    math_ans = solve_math(q)
    if math_ans:
        return {"text": math_ans, "image": None}

    # 3. BIOLOGY, CHEMISTRY, PHYSICS etc - use search
    if any(word in low for word in ["what is", "define", "explain", "photosynthesis", "mitosis", "cell", "atom", "gravity", "force", "energy", "biology", "chemistry", "physics"]):
        g_text = google_search(q)
        if g_text:
            return {"text": g_text, "image": None}

    # 4. GENERAL SEARCH
    g_text = google_search(q)
    if g_text:
        return {"text": g_text, "image": None}

    w_result = wiki_search(q)
    if w_result:
        return w_result

    today = datetime.now().strftime("%B %d, %Y")
    return {"text": f"📅 Today is {today}\n\nI searched for '{q}'\n\n✅ Try these examples:\n\n📐 MATH: 'Calculate 25 * 45' or 'What is 100 / 4?'\n🔬 BIOLOGY: 'What is photosynthesis?' or 'Define mitosis'\n⚗️ CHEMISTRY: 'What is an atom?'\n🌍 GEOGRAPHY: 'Capital of Nigeria?'\n👤 PEOPLE: 'Who is Wole Soyinka?'\n🎨 IMAGE: 'generate image of human cell'\n\nI can answer all subjects!", "image": None}

UI = """<!DOCTYPE html><html><head><title>cAI - School AI</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}body{background:#0a0a0a;color:#ececec;height:100vh;display:flex;flex-direction:column;overflow:hidden}#loader{position:fixed;inset:0;background:#050505;display:flex;align-items:center;justify-content:center;z-index:9999;transition:opacity 0.6s}#loader.hide{opacity:0;pointer-events:none}.logo-load{width:180px;height:180px;animation:spin 2.5s linear infinite;filter:drop-shadow(0 0 20px gold)}@keyframes spin{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}header{padding:12px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1a1a1a}#chat{flex:1;overflow:auto;padding:20px;max-width:760px;margin:0 auto;width:100%;display:flex;flex-direction:column}.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}.welcome h1{font-size:28px;font-weight:700;margin-bottom:8px}.welcome p{color:#888;font-size:14px;margin-bottom:20px}.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%;max-width:540px}.card{background:#151515;border:1px solid #222;border-radius:14px;padding:14px;cursor:pointer;text-align:left}.card:hover{background:#1c1c1c;border-color:gold}.bubble{padding:12px 16px;border-radius:20px;max-width:85%;margin:8px 0;white-space:pre-wrap;font-size:14.5px;line-height:1.6}.user{margin-left:auto;background:#fff;color:#000;border-bottom-right-radius:6px}.bot{background:#161616;border:1px solid #232323;border-bottom-left-radius:6px}.bot img{width:100%;max-width:400px;border-radius:12px;margin-top:10px;display:block}footer{border-top:1px solid #1a1a1a;padding:14px;display:flex;justify-content:center;background:#0a0a0a}.box{width:100%;max-width:760px;background:#181818;border:1px solid #2a2a2a;border-radius:24px;display:flex;align-items:center;padding:4px 6px 4px 14px}input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:10px 6px;font-size:15px}button.send{background:#fff;color:#000;border:none;width:32px;height:32px;border-radius:50%;cursor:pointer;font-weight:900}.btn{color:#555;font-size:11px;border:1px solid #222;padding:5px 12px;border-radius:16px;background:transparent;cursor:pointer;margin-left:6px}.btn-del{color:#ff5555;border-color:#ff555522}</style></head><body><div id="loader"><img src="/logo.png" class="logo-load" onerror="this.style.display='none'"></div><header><div style="display:flex;align-items:center;gap:8px"><img src="/logo.png" style="width:28px;height:28px;border-radius:50%" onerror="this.style.display='none'"><b style="color:gold">cAI School</b></div><div style="display:flex"><button class="btn btn-del" onclick="deleteFirstText()">Delete First</button><button class="btn" onclick="clearChat()">New Chat</button></div></header><div id="chat"></div><footer><div class="box"><input id="inp" placeholder="Ask Maths, Biology, or generate image..." onkeydown="if(event.key==='Enter')send()"><button class="send" onclick="send()">↑</button></div></footer><script>const SUGGESTIONS=[{icon:"📐",t:"Mathematics",d:"25 * 45 =?",p:"Calculate 25 * 45"},{icon:"🔬",t:"Biology",d:"Photosynthesis",p:"What is photosynthesis?"},{icon:"⚗️",t:"Chemistry",d:"What is atom?",p:"What is an atom? Explain simply"},{icon:"🎨",t:"Generate",d:"Human cell diagram",p:"generate image of human cell structure"}];function showWelcome(){let mots=["What subject today? 📚","Maths, Biology, Physics ready! ✨","Your School AI is ready! 💡"];let mot=mots[Math.floor(Math.random()*mots.length)];let chat=document.getElementById('chat');chat.innerHTML='<div class="welcome"><div style="color:gold;font-size:13px;margin-bottom:10px">'+mot+'</div><h1>Good morning 👋</h1><p>Maths • Biology • Chemistry • Physics • Images</p><div class="cards">'+SUGGESTIONS.map(s=>'<div class="card" onclick="quick(\\''+s.p+'\\')"><div>'+s.icon+'</div><div style=\\'font-weight:600;font-size:13px\\'>'+s.t+'</div><div style=\\'color:#666;font-size:11px\\'>'+s.d+'</div></div>').join('')+'</div></div>';}function quick(t){let w=document.querySelector('.welcome');if(w)w.remove();document.getElementById('inp').value=t;send();}window.onload=()=>{setTimeout(()=>{document.getElementById('loader').classList.add('hide');},2000);let saved=localStorage.getItem('cAI_school_final');if(saved&&saved.length>60){document.getElementById('chat').innerHTML=saved;}else{showWelcome();}};function saveChat(){if(!document.querySelector('.welcome')){localStorage.setItem('cAI_school_final',document.getElementById('chat').innerHTML);}}function clearChat(){document.getElementById('chat').innerHTML="";localStorage.removeItem('cAI_school_final');showWelcome();}function deleteFirstText(){let chat=document.getElementById('chat');let bubbles=chat.querySelectorAll('.bubble');if(bubbles.length>0){bubbles[0].remove();saveChat();}else{alert("No message!");}}async function send(){let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;let c=document.getElementById('chat');if(document.querySelector('.welcome')){document.querySelector('.welcome').remove();}c.innerHTML+='<div class="bubble user">'+t+'</div>';i.value='';c.scrollTop=99999;c.innerHTML+='<div class="bubble bot" id="temp">Thinking... 🧠</div>';c.scrollTop=99999;let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());let temp=document.getElementById('temp');if(temp)temp.remove();let imgHtml=r.image?'<img src="'+r.image+'"><br><a href="'+r.image+'" target="_blank" style="color:#888;font-size:11px;text-decoration:none">Download image</a>':'';c.innerHTML+='<div class="bubble bot">'+r.a+imgHtml+'</div>';c.scrollTop=99999;saveChat();}</script></body></html>
"""
@app.route('/')
def home(): return render_template_string(UI)
@app.route('/logo.png')
def logo():
    try: return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
    except: return "", 404
@app.route('/ask', methods=['POST'])
def ask():
    q = request.get_json().get('q','')
    result = smart_answer(q)
    return jsonify({"a": result["text"], "image": result["image"]})
if __name__=='__main__':
    app.run(port=5000)