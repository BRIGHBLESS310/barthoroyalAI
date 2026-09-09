from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os

app = Flask(__name__)
HEADERS = {"User-Agent": "cAI/1.0"}

def smart_answer(q):
    low = q.lower().strip()
    
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
        return {"text": f"Created: {prompt}", "image": img_url}

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
        return {"text": f"Result for '{q}'", "image": None}
    except:
        return {"text": "Try again", "image": None}

UI = """
<!DOCTYPE html><html><head>
<title>Companion</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,-apple-system,BlinkMacSystemFont,sans-serif}
body{background:#0a0a0a;color:#ececec;height:100vh;display:flex;flex-direction:column;overflow:hidden}
/* LOADING SPIN */
#loader{position:fixed;inset:0;background:#050505;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:9999;transition:opacity 0.8s ease}
#loader.hide{opacity:0;pointer-events:none}
.logo-load{width:190px;height:190px;animation:spin 2.5s linear infinite, float 2s ease-in-out infinite;filter:drop-shadow(0 0 25px gold)}
@keyframes spin{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}
@keyframes float{0%,100%{transform:translateY(0) rotateY(0deg)}50%{transform:translateY(-12px) rotateY(180deg)}}
.loader-text{margin-top:20px;font-size:24px;font-weight:800;color:gold;letter-spacing:2px}
/* HEADER - CLEAN LIKE CHROME */
header{padding:12px 16px;border-bottom:1px solid #1a1a1a;display:flex;justify-content:flex-end;align-items:center}
#chat{flex:1;overflow:auto;padding:20px;max-width:760px;margin:0 auto;width:100%;display:flex;flex-direction:column}
.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px;animation:fadeIn 0.6s}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.welcome h1{font-size:30px;font-weight:700;margin-bottom:8px;letter-spacing:-0.5px}
.welcome p{color:#888;font-size:14px;margin-bottom:28px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%;max-width:560px}
.card{background:#151515;border:1px solid #222;border-radius:14px;padding:14px;cursor:pointer;transition:0.2s;text-align:left}
.card:hover{background:#1c1c1c;border-color:#333}
.card.ic{font-size:20px;margin-bottom:4px}
.card.t{font-size:13px;font-weight:600}
.card.d{font-size:11px;color:#666;margin-top:2px}
.bubble{padding:12px 16px;border-radius:20px;max-width:84%;margin:8px 0;white-space:pre-wrap;line-height:1.5;font-size:14.5px}
.user{margin-left:auto;background:#fff;color:#000;border-bottom-right-radius:6px}
.bot{background:#161616;border:1px solid #232323;border-bottom-left-radius:6px}
.bot img{width:100%;max-width:400px;border-radius:12px;margin-top:10px;display:block}
footer{border-top:1px solid #1a1a1a;padding:14px 12px;display:flex;justify-content:center;background:#0a0a0a}
.box{width:100%;max-width:760px;background:#181818;border:1px solid #2a2a2a;border-radius:24px;display:flex;align-items:center;padding:4px 6px 4px 14px;transition:0.2s}
.box:focus-within{border-color:#444;background:#1e1e1e}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:10px 6px;font-size:15px}
button.send{background:#fff;color:#000;border:none;width:32px;height:32px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:16px}
#clear{background:transparent;color:#555;font-size:11px;border:1px solid #222;padding:5px 12px;border-radius:16px;cursor:pointer}
#clear:hover{color:#aaa;border-color:#333}
.mot{color:#aaa;font-size:12px;margin-bottom:10px;letter-spacing:0.5px}
</style></head><body>
<div id="loader">
  <img src="/logo.png" class="logo-load" onerror="this.style.display='none'">
  <div class="loader-text">cAI</div>
</div>
<header>
<button id="clear" onclick="clearChat()">New Chat</button>
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
 {icon:"🎨",t:"Create image",d:"Futuristic Lagos",p:"generate image of futuristic Lagos city"},
 {icon:"💡",t:"Ideas",d:"Business ideas",p:"Give me 5 business ideas"},
 {icon:"📚",t:"Learn",d:"History of Benin",p:"Tell me history of Benin Kingdom"},
 {icon:"✨",t:"Design",d:"Luxury logo",p:"generate image of luxury logo"}
];

function showWelcome(){
 let mots = ["What would you like to do today?","Ready to create something amazing? ✨","Your imagination is the limit. 🚀","Lets make magic today! 💡","What are we building today?"];
 let mot = mots[Math.floor(Math.random()*mots.length)];
 let chat=document.getElementById('chat');
 chat.innerHTML = '<div class="welcome"><div class="mot">'+mot+'</div><h1>Good morning 👋</h1><p>Chat, search, or generate images - I got you.</p><div class="cards">'+SUGGESTIONS.map(s=>'<div class="card" onclick="quick(\\''+s.p+'\\')"><div class="ic">'+s.icon+'</div><div class="t">'+s.t+'</div><div class="d">'+s.d+'</div></div>').join('')+'</div></div>';
}
function quick(t){ let w=document.querySelector('.welcome'); if(w) w.remove(); document.getElementById('inp').value=t; send(); }

window.onload = ()=>{
 setTimeout(()=>{ document.getElementById('loader').classList.add('hide'); }, 2500);
 let saved = localStorage.getItem('cAI_clean');
 if(saved && saved.length>60){ document.getElementById('chat').innerHTML = saved; }
 else { showWelcome(); }
};

function saveChat(){ if(!document.querySelector('.welcome')){ localStorage.setItem('cAI_clean', document.getElementById('chat').innerHTML); } }
function clearChat(){ document.getElementById('chat').innerHTML=""; localStorage.removeItem('cAI_clean'); showWelcome(); }

async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t) return;
 let c=document.getElementById('chat');
 if(document.querySelector('.welcome')){ document.querySelector('.welcome').remove(); }
 c.innerHTML+='<div class="bubble user">'+t+'</div>'; i.value=''; c.scrollTop=99999;
 c.innerHTML+='<div class="bubble bot" id="temp">...</div>'; c.scrollTop=99999;
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());
 let temp=document.getElementById('temp'); if(temp) temp.remove();
 let imgHtml = r.image? '<img src="'+r.image+'"><br><a href="'+r.image+'" target="_blank" style="color:#888;font-size:11px;text-decoration:none">Download</a>' : '';
 c.innerHTML+='<div class="bubble bot">'+r.a+imgHtml+'</div>'; c.scrollTop=99999; saveChat();
}
</script>
</body></html>
"""

@app.route('/')
def home(): return render_template_string(UI)

@app.route('/logo.png')
def logo():
    try:
        return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
    except:
        return "", 404

@app.route('/ask', methods=['POST'])
def ask():
    q = request.get_json().get('q','')
    result = smart_answer(q)
    return jsonify({"a": result["text"], "image": result["image"]})

if __name__=='__main__':
    app.run(port=5000)