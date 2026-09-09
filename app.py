from flask import Flask, request, jsonify, render_template_string
import requests, urllib.parse, random

app = Flask(__name__)
HEADERS = {"User-Agent": "companionAI-Benin/1.0"}

def smart_answer(q):
    low=q.lower()
    image_keywords = ["generate image", "create image", "make image", "draw", "generate a", "create a picture", "imagine", "picture of"]
    is_image = any(k in low for k in image_keywords) or low.startswith("image of")

    if is_image:
        prompt = q
        for k in ["generate image of", "generate image", "create image of", "create image", "make image of", "make image", "draw", "image of", "picture of", "imagine"]:
            if k in low:
                prompt = q.lower().split(k,1)[-1].strip()
                break
        if len(prompt) < 3: prompt = q
        safe_prompt = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed={abs(hash(q))%100000}&nologo=true"
        return {"text": f"🎨 Created: '{prompt}'", "image": img_url}

    if "how far" in low:
        return {"text": "How far padi! 🚀 Ready to create something amazing today?", "image": None}
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
        return {"text": f"I searched '{q}' - try rephrasing!", "image": None}
    except Exception as e:
        return {"text": f"Error: {str(e)[:100]}", "image": None}

MOTIVATIONS = [
    "What would you like to do today?",
    "Dream big, create bigger. ✨",
    "Your imagination is the limit. 🚀",
    "Every great idea starts with a single prompt.",
    "Ready to turn ideas into reality?",
    "Let's make something amazing today! 💡",
    "The future belongs to creators like you.",
    "What will you build today, legend? 👑"
]

UI = """<!DOCTYPE html><html><head>
<title>companionAI</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,sans-serif}
body{background:#0a0a0a;color:#ececec;height:100vh;display:flex;flex-direction:column}
header{padding:16px 20px;border-bottom:1px solid #1a1a1a;display:flex;justify-content:space-between;align-items:center;background:#0a0a0a}
header h2{font-weight:700;letter-spacing:-0.5px;font-size:20px;background:linear-gradient(90deg,#fff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
#chat{flex:1;overflow:auto;padding:20px;max-width:800px;margin:0 auto;width:100%;display:flex;flex-direction:column}
.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px 20px;animation:fadeIn 0.8s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.welcome h1{font-size:32px;font-weight:700;margin-bottom:12px;letter-spacing:-1px}
.welcome.sub{color:#888;font-size:16px;margin-bottom:32px;max-width:500px;line-height:1.5}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%;max-width:600px;margin-bottom:20px}
.card{background:#141414;border:1px solid #222;border-radius:16px;padding:16px;text-align:left;cursor:pointer;transition:all 0.2s}
.card:hover{background:#1a1a1a;border-color:#333;transform:translateY(-2px)}
.card.icon{font-size:22px;margin-bottom:8px}
.card.t{font-size:14px;font-weight:600;margin-bottom:4px}
.card.d{font-size:12px;color:#888}
.bubble{padding:14px 18px;border-radius:20px;max-width:85%;margin:10px 0;white-space:pre-wrap;line-height:1.6;font-size:15px}
.user{margin-left:auto;background:#fff;color:#000;border-bottom-right-radius:6px}
.bot{background:#1a1a1a;border:1px solid #222;border-bottom-left-radius:6px}
.bot img{width:100%;max-width:420px;border-radius:14px;margin-top:12px;display:block;border:1px solid #222}
footer{border-top:1px solid #1a1a1a;padding:16px;display:flex;justify-content:center;gap:8px;background:#0a0a0a}
.box{width:100%;max-width:800px;background:#141414;border:1px solid #222;border-radius:28px;display:flex;align-items:center;padding:6px 10px;transition:border-color 0.2s}
.box:focus-within{border-color:#555}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:12px 14px;font-size:16px}
button.send{background:#fff;border:none;width:36px;height:36px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px;transition:transform 0.1s}
button.send:active{transform:scale(0.92)}
#mic{background:#1a1a1a;border:1px solid #222;color:#fff}
#clear{background:transparent;color:#666;font-size:12px;border:1px solid #222;padding:6px 14px;border-radius:20px;cursor:pointer}
#clear:hover{color:#fff;border-color:#444}
.motivation{color:#a78bfa;font-weight:600;font-size:13px;margin-bottom:8px;letter-spacing:0.5px;text-transform:uppercase}
</style></head><body>
<header>
<h2>companionAI</h2>
<div><button id="clear" onclick="clearChat()">New Chat</button></div>
</header>
<div id="chat"></div>
<footer>
<div class="box">
<input id="inp" placeholder="Ask anything or generate an image..." onkeydown="if(event.key==='Enter')send()">
<button id="mic" onclick="startMic()">🎤</button>
<button class="send" onclick="send()">↑</button>
</div>
</footer>
<script>
const MOTIVATIONS = ["What would you like to do today?","Dream big, create bigger. ✨","Your imagination is the limit. 🚀","Every great idea starts with a single prompt.","Ready to turn ideas into reality?","Let's make something amazing today! 💡","The future belongs to creators like you.","What will you build today, legend? 👑"];
const SUGGESTIONS = [
 {icon:"🎨",t:"Create an image",d:"Generate futuristic Lagos city",prompt:"generate image of futuristic Lagos city at night, cyberpunk"},
 {icon:"💡",t:"Get inspired",d:"Motivational business ideas",prompt:"Give me 5 profitable business ideas in Benin"},
 {icon:"📚",t:"Learn something",d:"Who is the richest man in Africa?",prompt:"Who is the richest man in Africa?"},
 {icon:"✨",t:"Design",d:"Logo for my brand Barthoroyal",prompt:"generate image of luxury logo for Barthoroyal brand, gold and black"}
];

function showWelcome(){
 let mot = MOTIVATIONS[Math.floor(Math.random()*MOTIVATIONS.length)];
 let chat=document.getElementById('chat');
 chat.innerHTML = `
 <div class="welcome">
   <div class="motivation">${mot}</div>
   <h1>Good morning, Creator 👋</h1>
   <p class="sub">I'm companionAI - your partner for chat, search, and AI image generation. What are we building today?</p>
   <div class="cards">
     ${SUGGESTIONS.map(s=>`<div class="card" onclick="quick('${s.prompt.replace(/'/g,"\\'")}')"><div class="icon">${s.icon}</div><div class="t">${s.t}</div><div class="d">${s.d}</div></div>`).join('')}
   </div>
   <p style="color:#444;font-size:11px;margin-top:10px">Tip: Type "generate image of..." to create art instantly</p>
 </div>`;
}

function quick(t){
 let welcome=document.querySelector('.welcome');
 if(welcome) welcome.remove();
 document.getElementById('inp').value=t;
 send();
}

let recognition;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
 let SR = window.SpeechRecognition || window.webkitSpeechRecognition;
 recognition = new SR(); recognition.lang='en-NG';
 recognition.onresult=(e)=>{ document.getElementById('inp').value=e.results[0][0].transcript; send(); };
}
function startMic(){ if(recognition) recognition.start(); }

window.onload = ()=>{
 let saved = localStorage.getItem('companion_chat_v2');
 if(saved && saved.length>50){
   document.getElementById('chat').innerHTML = saved;
 } else {
   showWelcome();
 }
};

function saveChat(){
 if(!document.querySelector('.welcome')){
   localStorage.setItem('companion_chat_v2', document.getElementById('chat').innerHTML);
 }
}
function clearChat(){
 document.getElementById('chat').innerHTML="";
 localStorage.removeItem('companion_chat_v2');
 showWelcome();
}
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat');
 if(document.querySelector('.welcome')){ document.querySelector('.welcome').remove(); }
 c.innerHTML+=`<div class="bubble user">${t}</div>`; i.value=''; c.scrollTop=99999;
 c.innerHTML+=`<div class="bubble bot" id="temp">Thinking...</div>`; c.scrollTop=99999;
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());
 document.getElementById('temp')?.remove();
 let imgHtml = r.image? `<img src="${r.image}" loading="lazy"><br><a href="${r.image}" target="_blank" style="color:#a78bfa;font-size:12px;text-decoration:none">⬇ Download</a>` : '';
 c.innerHTML+=`<div class="bubble bot">${r.a}${imgHtml}</div>`; c.scrollTop=99999; saveChat();
}
</script>
</body></html>"""

@app.route('/')
def home():
    return render_template_string(UI, mots=MOTIVATIONS)

@app.route('/ask', methods=['POST'])
def ask():
    q=request.get_json().get('q','')
    result=smart_answer(q)
    return jsonify({"a": result["text"], "image": result["image"]})

if __name__=='__main__':
    app.run(port=5000)