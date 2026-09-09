from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os

app = Flask(__name__)
HEADERS = {"User-Agent": "cAI-Benin/1.0"}

def smart_answer(q):
    low = q.lower().strip()
    
    # === FIX 1: CREATOR MUST BE FIRST - NO WIKIPEDIA ===
    if "creator" in low or "who made you" in low or "who built you" in low or "who develop you" in low:
        return {"text": "My creator is Blessed Ovenseri 👑 - The genius behind cAI! He built me with passion from Benin, Edo State. CEO of Barthoroyal! 🚀🔥", "image": None}
    
    # === IMAGE GENERATION ===
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
    
    # === WIKIPEDIA ONLY IF NOT CREATOR QUESTION ===
    try:
        query = q.replace("who is","").replace("what is","").strip() or q
        # Don't search wikipedia if query is about creator
        if "creator" in query.lower():
            return {"text": "My creator is Blessed Ovenseri 👑", "image": None}
            
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
.logo-load{
  width:200px;height:200px;
  animation: spin 3s linear infinite, float 2s ease-in-out infinite, glow 2s ease-in-out infinite;
  filter:drop-shadow(0 0 25px gold);
  transform-style:preserve-3d;
}
@keyframes spin{
  0%{transform:rotateY(0deg) rotateZ(0deg)}
  50%{transform:rotateY(180deg) rotateZ(10deg)}
  100%{transform:rotateY(360deg) rotateZ(0deg)}
}
@keyframes float{0%,100%{transform:translateY(0) rotateY(0deg)}50%{transform:translateY(-15px) rotateY(180deg)}}
@keyframes glow{0%,100%{filter:drop-shadow(0 0 20px gold) brightness(1)}50%{filter:drop-shadow(0 0 40px gold) brightness(1.3)}}
.loader-text{margin-top:24px;font-size:28px;font-weight:900;letter-spacing:3px;color:gold;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.7}}
.loader-sub{color:#666;font-size:11px;margin-top:8px;letter-spacing:4px;text-transform:uppercase}
header{padding:14px 20px;border-bottom:1px solid #1a1a1a;display:flex;justify-content:space-between;align-items:center}
header h2{font-weight:900;font-size:22px;color:gold;display:flex;align-items:center;gap:10px}
header h2 img{width:36px;height:36px;border-radius:50%;animation:spin 4s linear infinite}
#chat{flex:1;overflow:auto;padding:20px;max-width:800px;margin:0 auto;width:100%;display:flex;flex-direction:column}
.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px}
.welcome h1{font-size:32px;font-weight:800;margin-bottom:10px}
.welcome p{color:#888;font-size:15px;margin-bottom:26px;max-width:520px;line-height:1.5}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%;max-width:600px}
.card{background:#141414;border:1px solid #222;border-radius:16px;padding:16px;text-align:left;cursor:pointer;transition:0.2s}
.card:hover{background:#1e1e1e;border-color:gold;transform:translateY(-2px)}
.bubble{padding:14px 18px;border-radius:20px;max-width:85%;margin:10px 0;white-space:pre-wrap;line-height:1.6;font-size:15px}
.user{margin-left:auto;background:#fff;color:#000;border-bottom-right-radius:6px}
.bot{background:#1a1a1a;border:1px solid #222;border-bottom-left-radius:6px}
.bot img{width:100%;max-width:420px;border-radius:14px;margin-top:12px;display:block}
footer{border-top:1px solid #1a1a1a;padding:16px;display:flex;justify-content:center;background:#0a0a0a}
.box{width:100%;max-width:800px;background:#141414;border:1px solid #222;border-radius:28px;display:flex;align-items:center;padding:6px 10px}
.box:focus-within{border-color:gold}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:12px 14px;font-size:16px}
button.send{background:gold;color:#000;border:none;width:36px;height:36px;border-radius:50%;cursor:pointer;font-weight:900}
#clear{background:transparent;color:#555;font-size:12px;border:1px solid #222;padding:6px 14px;border-radius:20px;cursor:pointer}
.mot{color:gold;font-weight:700;font-size:12px;margin-bottom:10px;letter-spacing:1px;text-transform:uppercase}
</style></head><body>
<div id="loader">
  <img src="/logo.png" class="logo-load" onerror="this.src='https://cdn-icons-png.flaticon.com/512/4712/4712109.png'">
  <div class="loader-text">cAI</div>
  <div class="loader-sub">By Blessed Ovenseri • Spinning...</div>
</div>
<header>
<h2><img src="/logo.png" onerror="this.style.display='none'"> cAI</h2>
<div><button id="clear" onclick="clearChat()">New Chat</button></div>
</header>
<div id="chat"></div>
<footer>
<div class="box">
<input id="inp" placeholder="Ask anything..." onkeydown="if(event.key==='Enter')send()">
<button class="send" onclick="send()">↑</button>
</div>
</footer>
<script>
const SUGGESTIONS = [
 {icon:"🎨",t:"Create an image",d:"Futuristic Lagos",p:"generate image of futuristic Lagos"},
 {icon:"💡",t:"Motivation",d:"Daily quote",p:"Give me a motivational quote"},
 {icon:"👑",t:"Creator",d:"Who is your creator?",p:"Who is your creator?"},
 {icon:"✨",t:"Design",d:"Royal logo",p:"generate image of luxury gold logo for cAI"}
];
function showWelcome(){
 let mots = ["What would you like to do today?","Dream big, create bigger. ✨","Your imagination is the limit. 🚀","Crafted by Blessed Ovenseri 👑","Ready to spin some magic? 🌀"];
 let mot = mots[Math.floor(Math.random()*mots.length)];
 let chat=document.getElementById('chat');
 chat.innerHTML = '<div class="welcome"><div class="mot">'+mot+'</div><h1>Good morning, Creator 👋</h1><p>I am <b>cAI</b> - built by <b>Blessed Ovenseri</b>. Chat, search, generate images.</p><div class="cards">'+SUGGESTIONS.map(s=>'<div class="card" onclick="quick(\\''+s.p+'\\')"><div>'+s.icon+'</div><div style=\\'font-weight:700\\'>'+s.t+'</div><div style=\\'color:#777;font-size:12px\\'>'+s.d+'</div></div>').join('')+'</div></div>';
}
function quick(t){ let w=document.querySelector('.welcome'); if(w) w.remove(); document.getElementById('inp').value=t; send(); }
window.onload = ()=>{
 setTimeout(()=>{ document.getElementById('loader').classList.add('hide'); }, 3000);
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