from flask import Flask, request, jsonify, render_template_string
import requests, urllib.parse

app = Flask(__name__)
HEADERS = {"User-Agent": "companionAI-Benin/1.0"}

def smart_answer(q):
    low=q.lower()
    image_keywords = ["generate image", "create image", "make image", "draw", "generate a", "create a picture", "imagine"]
    is_image = any(k in low for k in image_keywords) or low.startswith("image of") or low.startswith("picture of")

    if is_image:
        prompt = q
        for k in ["generate image of", "generate image", "create image of", "create image", "make image of", "make image", "draw", "image of", "picture of"]:
            if k in low:
                prompt = q.lower().split(k,1)[-1].strip()
                break
        if len(prompt) < 3:
            prompt = q
        safe_prompt = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed={abs(hash(q))%100000}&nologo=true"
        return {"text": f"🎨 Generated: '{prompt}'", "image": img_url}

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
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}
body{background:#0f0f0f;color:#ececec;height:100vh;display:flex;flex-direction:column}
header{padding:14px 16px;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center}
.main{flex:1;display:flex;overflow:hidden}
#left{width:320px;background:#0a0a0a;border-right:1px solid #222;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}
#left h3{font-size:13px;color:#888;letter-spacing:1px;text-transform:uppercase}
.gen-card{background:#151515;border:1px solid #222;border-radius:14px;overflow:hidden}
.gen-card img{width:100%;display:block}
.gen-card.cap{padding:8px 10px;font-size:11px;color:#aaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#center{flex:1;display:flex;flex-direction:column}
#chat{flex:1;overflow:auto;padding:20px}
.bubble{padding:14px 16px;border-radius:18px;max-width:85%;margin:10px 0;white-space:pre-wrap;line-height:1.6}
.user{margin-left:auto;background:#fff;color:#000}
.bot{background:#1e1e1e;border:1px solid #2a2a2a}
.bot img{width:100%;max-width:350px;border-radius:12px;margin-top:10px;display:block;border:1px solid #333}
footer{border-top:1px solid #222;padding:12px;display:flex;justify-content:center;flex-direction:column;align-items:center;gap:8px}
.box{width:100%;max-width:700px;background:#1e1e1e;border:1px solid #333;border-radius:28px;display:flex;align-items:center;padding:6px 10px}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:12px;font-size:16px}
button{background:#fff;border:none;width:38px;height:38px;border-radius:50%;cursor:pointer;margin-left:4px;font-size:18px}
#mic{background:#ff3b30;color:#fff} #mic.listening{background:#10a37f;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
#clear{background:#333;color:#fff;font-size:11px;width:auto;padding:0 10px;border-radius:10px}
.hint{display:flex;gap:6px;flex-wrap:wrap;max-width:700px;width:100%}
.hint span{background:#1a1a1a;border:1px solid #2a2a2a;padding:5px 9px;border-radius:20px;font-size:10px;cursor:pointer;color:#aaa}
@media(max-width:800px){#left{width:120px} #left h3{font-size:10px}.gen-card.cap{font-size:9px}}
</style></head><body>
<header>
<h2>companionAI 🎨</h2>
<div><button id="clear" onclick="clearChat()">Clear All</button></div>
</header>
<div class="main">
<div id="left">
<h3>🎨 Generated Images (Vertical)</h3>
<div id="imageList" style="display:flex;flex-direction:column;gap:12px"></div>
</div>
<div id="center">
<div id="chat"></div>
<footer>
<div class="hint">
<span onclick="quick('generate image of futuristic Lagos')">Lagos</span>
<span onclick="quick('generate image of African king')">King</span>
<span onclick="quick('generate image of cute anime girl')">Anime</span>
<span onclick="quick('who is Burna Boy')">Burna</span>
</div>
<div class="box">
<input id="inp" placeholder="Type 'generate image of...' " onkeydown="if(event.key==='Enter')send()">
<button id="mic" onclick="startMic()">🎤</button>
<button onclick="send()">↑</button>
</div>
</footer>
</div>
</div>
<script>
function quick(t){ document.getElementById('inp').value=t; send(); }
let recognition;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
 let SR = window.SpeechRecognition || window.webkitSpeechRecognition;
 recognition = new SR(); recognition.lang='en-NG';
 recognition.onstart=()=>{document.getElementById('mic').classList.add('listening');}
 recognition.onend=()=>{document.getElementById('mic').classList.remove('listening');}
 recognition.onresult=(e)=>{ document.getElementById('inp').value=e.results[0][0].transcript; send(); };
}
function startMic(){ if(recognition) recognition.start(); }
window.onload = ()=>{
 let saved = localStorage.getItem('companion_chat');
 if(saved){ document.getElementById('chat').innerHTML = saved; }
 let savedImg = localStorage.getItem('companion_images');
 if(savedImg){ document.getElementById('imageList').innerHTML = savedImg; }
 document.getElementById('chat').scrollTop = 99999;
};
function saveAll(){
  localStorage.setItem('companion_chat', document.getElementById('chat').innerHTML);
  localStorage.setItem('companion_images', document.getElementById('imageList').innerHTML);
}
function clearChat(){
 if(confirm("Clear everything?")){
   document.getElementById('chat').innerHTML="";
   document.getElementById('imageList').innerHTML="";
   localStorage.clear();
 }
}
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat');
 let list=document.getElementById('imageList');
 c.innerHTML+=`<div class="bubble user">${t}</div>`; i.value=''; saveAll(); c.scrollTop=99999;
 c.innerHTML+=`<div class="bubble bot" id="temp">🎨 Generating...</div>`;
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());
 document.getElementById('temp')?.remove();
 let imgHtml = r.image? `<img src="${r.image}" loading="lazy"><br><a href="${r.image}" target="_blank" style="color:#a78bfa;font-size:12px">⬇ Download</a>` : '';
 c.innerHTML+=`<div class="bubble bot">${r.a}${imgHtml}</div>`;
 // ADD TO LEFT VERTICAL LIST IF IT'S AN IMAGE
 if(r.image && r.image.includes('pollinations')){
   list.innerHTML = `<div class="gen-card"><img src="${r.image}"><div class="cap">${t.substring(0,40)}</div></div>` + list.innerHTML;
 }
 c.scrollTop=99999; saveAll();
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