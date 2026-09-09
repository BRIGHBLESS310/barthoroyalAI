from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os

app = Flask(__name__)
HEADERS = {"User-Agent": "cAI-Benin/1.0"}

def smart_answer(q):
    low = q.lower().strip()
    # CREATOR LOGIC - MUST ANSWER BLESSED OVENSERI
    if any(x in low for x in ["who is your creator", "who created you", "who made you", "who built you", "who is your maker", "who is your owner", "who develop you", "who is your father"]):
        return {"text": "My creator is Blessed Ovenseri 👑 - The genius behind cAI! He built me with passion from Benin, Edo State. The CEO of Barthoroyal! 🚀", "image": None}
    if "blessed ovenseri" in low or "blessed" in low and "ovenseri" in low:
        return {"text": "Blessed Ovenseri is my creator - a visionary developer, the mind behind cAI and Barthoroyal! 👑🔥", "image": None}

    image_keywords = ["generate image", "create image", "make image", "draw", "imagine", "picture of", "image of"]
    is_image = any(k in low for k in image_keywords)

    if is_image:
        prompt = q
        for k in ["generate image of", "generate image", "create image of", "create image", "make image of", "make image", "draw", "image of", "picture of", "imagine"]:
            if k in low:
                prompt = q.lower().split(k, 1)[-1].strip()
                break
        if len(prompt) < 3: prompt = q
        safe_prompt = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed={abs(hash(q))%100000}&nologo=true"
        return {"text": f"🎨 Created: '{prompt}'", "image": img_url}

    if "how far" in low:
        return {"text": "How far padi! Ready to create something amazing today? 🚀", "image": None}
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
        return {"text": f"Result for '{q}' - try again!", "image": None}
    except:
        return {"text": "Network error, try again", "image": None}

UI = """
<!DOCTYPE html><html><head>
<title>cAI by Blessed Ovenseri</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}
body{background:#0a0a0a;color:#ececec;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#loader{position:fixed;inset:0;background:#050505;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:9999;transition:opacity 0.8s ease}
#loader.hide{opacity:0;pointer-events:none}
.logo-load{width:200px;height:200px;animation:float 2s ease-in-out infinite;filter:drop-shadow(0 0 20px gold)}
@keyframes float{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-12px) scale(1.05)}}
.loader-text{margin-top:20px;font-size:28px;font-weight:900;letter-spacing:3px;color:gold}
.loader-sub{color:#666;font-size:11px;margin-top:8px;letter-spacing:4px;text-transform:uppercase}
header{padding:14px 20px;border-bottom:1px solid #1a1a1a;display:flex;justify-content:space-between;align-items:center}
header h2{font-weight:900;font-size:22px;color:gold;display:flex;align-items:center;gap:10px;letter-spacing:1px}
header h2 img{width:36px;height:36px;border-radius:50%}
#chat{flex:1;overflow:auto;padding:20px;max-width:800px;margin:0 auto;width:100%;display:flex;flex-direction:column}
.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px;animation:fadeIn 0.8s}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.welcome h1{font-size:32px;font-weight:800;margin-bottom:10px}
.welcome p{color:#888;font-size:15px;margin-bottom:26px;max-width:520px;line-height:1.5}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%;max-width:600px}
.card{background:#141414;border:1px solid #222;border-radius:16px;padding:16px;text-align:left;cursor:pointer;transition:0.2s}
.card:hover{background:#1e1e1e;border-color:gold;transform:translateY(-2px)}
.card.ic{font-size:22px;margin-bottom:6px}
.card.t{font-size:14px;font-weight:700}
.card.d{font-size:12px;color:#777;margin-top:3px}
.bubble{padding:14px 18px;border-radius:20px;max-width:85%;margin:10px 0;white-space:pre-wrap;line-height:1.6;font-size:15px}
.user{margin-left:auto;background:#fff;color:#000;border-bottom-right-radius:6px}
.bot{background:#1a1a1a;border:1px solid #222;border-bottom-left-radius:6px}
.bot img{width:100%;max-width:420px;border-radius:14px;margin-top:12px;display:block}
footer{border-top:1px solid #1a1a1a;padding:16px;display:flex;justify-content:center;background:#0a0a0a}
.box{width:100%;max-width:800px;background:#141414;border:1px solid #222;border-radius:28px;display:flex;align-items:center;padding:6px 10px}
.box:focus-within{border-color:gold}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:12px 14px;font-size:16px}
button.send{background:gold;color:#000;border:none;width:36px;height:36px;border-radius:50%;cursor:pointer;font-weight:900;font-size:18px}
#mic{background:#1a1a1a;border:1px solid #222;color:#fff;width:36px;height:36px;border-radius:50%;cursor:pointer;margin-right:4px}
#clear{background:transparent;color:#555;font-size:12px;border:1px solid #222;padding:6px 14px;border-radius:20px;cursor:pointer}
.mot{color:gold;font-weight:700;font-size:12px;margin-bottom:10px;letter-spacing:1px;text-transform:uppercase}
</style></head><body>
<div id="loader">
  <img src="/logo.png" class="logo-load" onerror="this.style.display='none'; document.getElementById('fb').style.display='block'">
  <div id="fb" style="display:none;width:140px;height:140px;background:radial-gradient(circle,gold,#000);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:40px;color:#000">cAI</div>
  <div class="loader-text">cAI</div>
  <div class="loader-sub">By Blessed Ovenseri</div>
</div>
<header>
<h2><img src="/logo.png" onerror="this.style.display='none'"> cAI</h2>
<div><button id="clear" onclick="clearChat()">New Chat</button></div>
</header>
<div id="chat"></div>
<footer>
<div class="box">
<input id="inp" placeholder="Ask anything or generate image..." onkeydown="if(event.key==='Enter')send()">
<button id="mic" onclick="startMic()">🎤</button>
<button class="send" onclick="send()">↑</button>
</div>
</footer>
<script>
const SUGGESTIONS = [
 {icon:"🎨",t:"Create an image",d:"Futuristic Lagos",p:"generate image of futuristic Lagos city at night"},
 {icon:"💡",t:"Inspiration",d:"Motivational quote",p:"Give me a motivational quote for today"},
 {icon:"📚",t:"Learn",d:"Who is my creator?",p:"Who is your creator?"},
 {icon:"✨",t:"Design",d:"Royal logo",p:"generate image of luxury gold logo for cAI"}
];

function showWelcome(){
 let mots = ["What would you like to do today?","Dream big, create bigger. ✨","Your imagination is the limit. 🚀","Every great idea starts with a prompt.","Ready to turn ideas into reality?","Lets make something amazing today! 💡","Crafted by Blessed Ovenseri 👑"];
 let mot = mots[Math.floor(Math.random()*mots.length)];
 let chat=document.getElementById('chat');
 chat.innerHTML = '<div class="welcome"><div class="mot">'+mot+'</div><h1>Good morning, Creator 👋</h1><p>I am <b>cAI</b> - built by <b>Blessed Ovenseri</b>. Chat, search, and generate images.</p><div class="cards">'+SUGGESTIONS.map(s=>'<div class="card" onclick="quick(\\''+s.p+'\\')"><div class="ic">'+s.icon+'</div><div class="t">'+s.t+'</div><div class="d">'+s.d+'</div></div>').join('')+'</div></div>';
}
function quick(t){ let w=document.querySelector('.welcome'); if(w) w.remove(); document.getElementById('inp').value=t; send(); }
let recognition;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
 let SR = window.SpeechRecognition || window.webkitSpeechRecognition;
 recognition = new SR(); recognition.lang='en-NG';
 recognition.onresult=(e)=>{ document.getElementById('inp').value=e.results[0][0].transcript; send(); };
}
function startMic(){ if(recognition) recognition.start(); }

window.onload = ()=>{
 setTimeout(()=>{ document.getElementById('loader').classList.add('hide'); }, 2800);
 let saved = localStorage.getItem('cAI_chat');
 if(saved && saved.length>60){ document.getElementById('chat').innerHTML = saved; }
 else { showWelcome(); }
};
function saveChat(){ if(!document.querySelector('.welcome')){ localStorage.setItem('cAI_chat', document.getElementById('chat').innerHTML); } }
function clearChat(){ document.getElementById('chat').innerHTML=""; localStorage.removeItem('cAI_chat'); showWelcome(); }

async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t) return;
 let c=document.getElementById('chat');
 if(document.querySelector('.welcome')){ document.querySelector('.welcome').remove(); }
 c.innerHTML+='<div class="bubble user">'+t+'</div>'; i.value=''; c.scrollTop=99999;
 c.innerHTML+='<div class="bubble bot" id="temp">Thinking...</div>'; c.scrollTop=99999;
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());
 let temp=document.getElementById('temp'); if(temp) temp.remove();
 let imgHtml = r.image? '<img src="'+r.image+'"><br><a href="'+r.image+'" target="_blank" style="color:gold;font-size:12px;text-decoration:none">⬇ Download</a>' : '';
 c.innerHTML+='<div class="bubble bot">'+r.a+imgHtml+'</div>'; c.scrollTop=99999; saveChat();
}
</script>
</body></html>
"""

@app.route('/')
def home(): return render_template_string(UI)

@app.route('/logo.png')
def logo():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'logo.png')

@app.route('/ask', methods=['POST'])
def ask():
    q = request.get_json().get('q','')
    result = smart_answer(q)
    return jsonify({"a": result["text"], "image": result["image"]})

if __name__=='__main__':
    app.run(port=5000)
