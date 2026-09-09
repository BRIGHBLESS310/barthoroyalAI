from flask import Flask, request, jsonify, render_template_string
import requests, urllib.parse

app = Flask(__name__)
HEADERS = {"User-Agent": "companionAI-Benin/1.0"}

def smart_answer(q):
    low=q.lower()
    # CHECK IF NA IMAGE GENERATION
    image_keywords = ["generate image", "create image", "make image", "draw", "generate a", "create a picture", "imagine"]
    is_image = any(k in low for k in image_keywords) or low.startswith("image of") or low.startswith("picture of")

    if is_image:
        # Extract the prompt
        prompt = q
        for k in ["generate image of", "generate image", "create image of", "create image", "make image of", "make image", "draw", "image of", "picture of"]:
            if k in low:
                prompt = q.lower().split(k,1)[-1].strip()
                break
        if len(prompt) < 3:
            prompt = q
        # Use Pollinations free AI
        safe_prompt = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed={abs(hash(q))%100000}&nologo=true"
        return {"text": f"🎨 Generated image for: '{prompt}'\n\nHere is your image 👇", "image": img_url}

    if "how far" in low:
        return {"text": "How far padi! Your chat dey save now!", "image": None}
    try:
        query = q.replace("who is","").replace("what is","").strip() or q
        query_enc = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query_enc}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code==200:
            data=r.json()
            text = data.get('extract','')
            img = data.get('thumbnail',{}).get('source') or data.get('originalimage',{}).get('source')
            title = data.get('title','')
            return {"text": f"{text}\n\nSource: {title}", "image": img}
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query_enc}&format=json"
        s=requests.get(search_url, headers=HEADERS, timeout=10).json()
        if s.get('query',{}).get('search'):
            title=s['query']['search'][0]['title']
            url2=f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
            r2=requests.get(url2, headers=HEADERS, timeout=10)
            if r2.status_code==200:
                data=r2.json()
                img = data.get('thumbnail',{}).get('source') or data.get('originalimage',{}).get('source')
                return {"text": f"{data.get('extract','')}\n\nSource: {data.get('title','')}", "image": img}
        return {"text": f"I search '{q}' - try again!", "image": None}
    except Exception as e:
        return {"text": f"Error: {str(e)[:100]}", "image": None}

UI = """<!DOCTYPE html><html><head>
<title>companionAI</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='white'/><text x='8' y='65' font-family='Arial' font-size='38' font-weight='400' fill='black'>c</text><text x='28' y='65' font-family='Arial' font-size='42' font-weight='900' fill='black'>A</text><text x='62' y='70' font-family='Arial' font-size='58' font-weight='300' fill='black'>I</text></svg>">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}
body{background:#0f0f0f;color:#ececec;height:100vh;display:flex;flex-direction:column}
header{padding:16px;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center}
#chat{flex:1;overflow:auto;padding:20px;max-width:900px;margin:0 auto;width:100%}
.bubble{padding:14px 16px;border-radius:18px;max-width:85%;margin:10px 0;white-space:pre-wrap;line-height:1.6}
.user{margin-left:auto;background:#fff;color:#000}
.bot{background:#1e1e1e;border:1px solid #2a2a2a}
.bot img{width:100%;max-width:400px;border-radius:12px;margin-top:10px;display:block;border:1px solid #333}
footer{border-top:1px solid #222;padding:12px;display:flex;justify-content:center;gap:8px;flex-direction:column;align-items:center}
.box{width:100%;max-width:900px;background:#1e1e1e;border:1px solid #333;border-radius:28px;display:flex;align-items:center;padding:6px 10px}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:12px;font-size:16px}
button{background:#fff;border:none;width:38px;height:38px;border-radius:50%;cursor:pointer;margin-left:4px;font-size:18px}
#mic{background:#ff3b30;color:#fff} #mic.listening{background:#10a37f;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
#clear{background:#333;color:#fff;font-size:12px;width:auto;padding:0 12px;border-radius:12px}
.hint{max-width:900px;width:100%;display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px}
.hint span{background:#1a1a1a;border:1px solid #2a2a2a;padding:6px 10px;border-radius:20px;font-size:11px;cursor:pointer;color:#aaa}
.hint span:hover{background:#fff;color:#000}
</style></head><body>
<header>
<h2>companionAI 🎨</h2>
<div><button id="clear" onclick="clearChat()">Clear</button> <span style="color:#10a37f;font-size:12px">● Saved</span></div>
</header>
<div id="chat"></div>
<footer>
<div class="hint">
<span onclick="quick('generate image of futuristic Lagos city')">🎨 Lagos City</span>
<span onclick="quick('generate image of African king with golden crown')">👑 African King</span>
<span onclick="quick('generate image of cute cat wearing agbada')">🐱 Cat Agbada</span>
<span onclick="quick('who is Wizkid')">❓ Wizkid</span>
</div>
<div class="box">
<input id="inp" placeholder="Ask or say 'generate image of...' " onkeydown="if(event.key==='Enter')send()">
<button id="mic" onclick="startMic()">🎤</button>
<button onclick="send()">↑</button>
</div>
</footer>
<script>
function quick(t){ document.getElementById('inp').value=t; send(); }
let recognition;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
 let SR = window.SpeechRecognition || window.webkitSpeechRecognition;
 recognition = new SR(); recognition.lang='en-NG';
 recognition.onstart=()=>{document.getElementById('mic').classList.add('listening'); document.getElementById('mic').innerText='🔴';}
 recognition.onend=()=>{document.getElementById('mic').classList.remove('listening'); document.getElementById('mic').innerText='🎤';}
 recognition.onresult=(e)=>{ document.getElementById('inp').value=e.results[0][0].transcript; send(); };
}
function startMic(){ if(recognition) recognition.start(); }
window.onload = ()=>{
 let saved = localStorage.getItem('companion_chat');
 if(saved){ document.getElementById('chat').innerHTML = saved; document.getElementById('chat').scrollTop = 99999; }
};
function saveChat(){ localStorage.setItem('companion_chat', document.getElementById('chat').innerHTML); }
function clearChat(){
 if(confirm("Clear chat?")){
   document.getElementById('chat').innerHTML="";
   localStorage.removeItem('companion_chat');
 }
}
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class="bubble user">${t}</div>`; i.value=''; saveChat(); c.scrollTop=99999;
 c.innerHTML+=`<div class="bubble bot" id="temp">🎨 Generating...</div>`; c.scrollTop=99999;
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());
 document.getElementById('temp')?.remove();
 let imgHtml = r.image? `<img src="${r.image}" loading="lazy" onerror="this.style.display='none'"><br><a href="${r.image}" target="_blank" style="color:#a78bfa;font-size:12px">⬇ Download Image</a>` : '';
 c.innerHTML+=`<div class="bubble bot">${r.a}${imgHtml}</div>`; c.scrollTop=99999; saveChat();
 if('speechSynthesis' in window){ speechSynthesis.cancel(); let u=new SpeechSynthesisUtterance(r.a.substring(0,300)); u.lang='en-NG'; speechSynthesis.speak(u); }
}
</script>
</body></html>"""

@app.route('/')
def home(): return render_template_string(UI)
@app.route('/ask', methods=['POST'])
def ask():
    q=request.get_json().get('q','')
    result=smart_answer(q)
    return jsonify({"a": result["text"], "image": result["image"]})

if __name__=='__main__':
    app.run(port=5000)