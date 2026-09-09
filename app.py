from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0"}

def google_search(q):
    try:
        r = requests.get(f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1&skip_disambig=1", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = r.json()
        if data.get('AbstractText'):
            return f"{data['AbstractText']}\n\nSource: DuckDuckGo"
        if data.get('RelatedTopics'):
            for topic in data['RelatedTopics'][:2]:
                if isinstance(topic, dict) and topic.get('Text'):
                    return f"{topic['Text'][:700]}\n\nSource: DuckDuckGo"
        wiki_search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json"
        r2 = requests.get(wiki_search_url, headers=HEADERS, timeout=8)
        d2 = r2.json()
        if d2.get('query',{}).get('search'):
            snippet = d2['query']['search'][0]['snippet']
            clean = BeautifulSoup(snippet, 'html.parser').get_text()
            return f"{clean[:700]}\n\nSource: Wikipedia Search"
        return None
    except:
        return None

def wiki_search(q):
    try:
        query = q.replace("who is","").replace("what is","").replace("tell me about","").strip() or q
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
        return {"text": f"✅ Created: {prompt}", "image": img_url}
    g_text = google_search(q)
    if g_text:
        return {"text": g_text, "image": None}
    w_result = wiki_search(q)
    if w_result:
        return w_result
    today = datetime.now().strftime("%B %d, %Y")
    return {"text": f"📅 Today is {today}\n\nI searched for '{q}' but live Google news is blocked on free hosting (Google bot protection).\n\n✅ TRY THESE - THEY WORK 100%:\n\n• Who is Bola Ahmed Tinubu?\n• History of Benin Kingdom\n• What is artificial intelligence?\n• generate image of futuristic Lagos\n\nFor latest Nigeria news, check google.com directly!", "image": None}

UI = """<!DOCTYPE html><html><head><title>cAI</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}body{background:#0a0a0a;color:#ececec;height:100vh;display:flex;flex-direction:column;overflow:hidden}#loader{position:fixed;inset:0;background:#050505;display:flex;align-items:center;justify-content:center;z-index:9999;transition:opacity 0.6s}#loader.hide{opacity:0;pointer-events:none}.logo-load{width:180px;height:180px;animation:spin 2.5s linear infinite;filter:drop-shadow(0 0 20px gold)}@keyframes spin{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}header{padding:12px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1a1a1a}#chat{flex:1;overflow:auto;padding:20px;max-width:760px;margin:0 auto;width:100%;display:flex;flex-direction:column}.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}.welcome h1{font-size:30px;font-weight:700;margin-bottom:8px}.welcome p{color:#888;font-size:14px;margin-bottom:26px}.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%;max-width:540px}.card{background:#151515;border:1px solid #222;border-radius:14px;padding:14px;cursor:pointer;text-align:left}.card:hover{background:#1c1c1c;border-color:gold}.bubble{padding:12px 16px;border-radius:20px;max-width:84%;margin:8px 0;white-space:pre-wrap;font-size:14.5px;line-height:1.5}.user{margin-left:auto;background:#fff;color:#000;border-bottom-right-radius:6px}.bot{background:#161616;border:1px solid #232323;border-bottom-left-radius:6px}.bot img{width:100%;max-width:400px;border-radius:12px;margin-top:10px;display:block}footer{border-top:1px solid #1a1a1a;padding:14px;display:flex;justify-content:center;background:#0a0a0a}.box{width:100%;max-width:760px;background:#181818;border:1px solid #2a2a2a;border-radius:24px;display:flex;align-items:center;padding:4px 6px 4px 14px}input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:10px 6px;font-size:15px}button.send{background:#fff;color:#000;border:none;width:32px;height:32px;border-radius:50%;cursor:pointer;font-weight:900}.btn{color:#555;font-size:11px;border:1px solid #222;padding:5px 12px;border-radius:16px;background:transparent;cursor:pointer;margin-left:6px}.btn-del{color:#ff5555;border-color:#ff555522}</style></head><body><div id="loader"><img src="/logo.png" class="logo-load" onerror="this.style.display='none'"></div><header><div style="display:flex;align-items:center;gap:8px"><img src="/logo.png" style="width:28px;height:28px;border-radius:50%" onerror="this.style.display='none'"><b style="color:gold">cAI</b></div><div style="display:flex"><button class="btn btn-del" onclick="deleteFirstText()">Delete First</button><button class="btn" onclick="clearChat()">New Chat</button></div></header><div id="chat"></div><footer><div class="box"><input id="inp" placeholder="Search Wikipedia or generate image..." onkeydown="if(event.key==='Enter')send()"><button class="send" onclick="send()">↑</button></div></footer><script>const SUGGESTIONS=[{icon:"🔍",t:"Wikipedia",d:"Bola Tinubu",p:"Who is Bola Ahmed Tinubu?"},{icon:"🎨",t:"Create image",d:"Futuristic Lagos",p:"generate image of futuristic Lagos city"},{icon:"📚",t:"Benin History",d:"Benin Kingdom",p:"History of Benin Kingdom"},{icon:"💡",t:"Explain AI",d:"How AI works",p:"What is artificial intelligence?"}];function showWelcome(){let mots=["What would you like to do today?","Wikipedia + Image Generation ✨","Ready to create? 💡"];let mot=mots[Math.floor(Math.random()*mots.length)];let chat=document.getElementById('chat');chat.innerHTML='<div class="welcome"><div class="mot">'+mot+'</div><h1>Good morning 👋</h1><p>Wikipedia search + AI image generation.</p><div class="cards">'+SUGGESTIONS.map(s=>'<div class="card" onclick="quick(\\''+s.p+'\\')"><div>'+s.icon+'</div><div style=\\'font-weight:600;font-size:13px\\'>'+s.t+'</div><div style=\\'color:#666;font-size:11px\\'>'+s.d+'</div></div>').join('')+'</div></div>';}function quick(t){let w=document.querySelector('.welcome');if(w)w.remove();document.getElementById('inp').value=t;send();}window.onload=()=>{setTimeout(()=>{document.getElementById('loader').classList.add('hide');},2000);let saved=localStorage.getItem('cAI_final_all');if(saved&&saved.length>60){document.getElementById('chat').innerHTML=saved;}else{showWelcome();}};function saveChat(){if(!document.querySelector('.welcome')){localStorage.setItem('cAI_final_all',document.getElementById('chat').innerHTML);}}function clearChat(){document.getElementById('chat').innerHTML="";localStorage.removeItem('cAI_final_all');showWelcome();}function deleteFirstText(){let chat=document.getElementById('chat');let bubbles=chat.querySelectorAll('.bubble');if(bubbles.length>0){bubbles[0].remove();saveChat();}else{alert("No message!");}}async function send(){let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;let c=document.getElementById('chat');if(document.querySelector('.welcome')){document.querySelector('.welcome').remove();}c.innerHTML+='<div class="bubble user">'+t+'</div>';i.value='';c.scrollTop=99999;c.innerHTML+='<div class="bubble bot" id="temp">Searching...</div>';c.scrollTop=99999;let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());let temp=document.getElementById('temp');if(temp)temp.remove();let imgHtml=r.image?'<img src="'+r.image+'"><br><a href="'+r.image+'" target="_blank" style="color:#888;font-size:11px;text-decoration:none">Download</a>':'';c.innerHTML+='<div class="bubble bot">'+r.a+imgHtml+'</div>';c.scrollTop=99999;saveChat();}</script></body></html>
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