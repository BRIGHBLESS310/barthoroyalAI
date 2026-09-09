from flask import Flask, request, jsonify, render_template_string
import requests, urllib.parse

app = Flask(__name__)
HEADERS = {"User-Agent": "companionAI-Benin/1.0"}

def smart_answer(q):
    low=q.lower()
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
.bot img{width:100%;max-width:350px;border-radius:12px;margin-top:10px;display:block}
footer{border-top:1px solid #222;padding:12px;display:flex;justify-content:center;gap:8px}
.box{width:100%;max-width:900px;background:#1e1e1e;border:1px solid #333;border-radius:28px;display:flex;align-items:center;padding:6px 10px}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:12px;font-size:16px}
button{background:#fff;border:none;width:38px;height:38px;border-radius:50%;cursor:pointer;margin-left:4px;font-size:18px}
#mic{background:#ff3b30;color:#fff} #mic.listening{background:#10a37f;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
#clear{background:#333;color:#fff;font-size:12px;width:auto;padding:0 12px;border-radius:12px}
.nav{display:flex;gap:8px}
.nav a{background:#222;color:#fff;padding:8px 14px;border-radius:20px;text-decoration:none;font-size:12px;border:1px solid #333}
.nav a:hover{background:#fff;color:#000}
</style></head><body>
<header>
<h2>companionAI</h2>
<div class="nav"><a href="/generate-image">🎨 Image</a><a href="/game">🎮 Game</a><button id="clear" onclick="clearChat()">Clear</button></div>
</header>
<div id="chat"></div>
<footer>
<div class="box">
<input id="inp" placeholder="Ask..." onkeydown="if(event.key==='Enter')send()">
<button id="mic" onclick="startMic()">🎤</button>
<button onclick="send()">↑</button>
</div>
</footer>
<script>
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
 if(confirm("You wan clear all chat?")){
   document.getElementById('chat').innerHTML="";
   localStorage.removeItem('companion_chat');
 }
}
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class="bubble user">${t}</div>`; i.value=''; saveChat();
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());
 let imgHtml = r.image? `<img src="${r.image}" onerror="this.style.display='none'">` : '';
 c.innerHTML+=`<div class="bubble bot">${r.a}${imgHtml}</div>`; c.scrollTop=99999; saveChat();
 if('speechSynthesis' in window){ speechSynthesis.cancel(); let u=new SpeechSynthesisUtterance(r.a.substring(0,300)); u.lang='en-NG'; speechSynthesis.speak(u); }
}
</script>
</body></html>"""

IMAGE_UI = """<!DOCTYPE html><html><head><title>Barthoroyal Image AI</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}
body{background:#0a0a0a;color:#fff;min-height:100vh}
header{padding:18px 22px;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center}
a{color:#fff;text-decoration:none;background:#222;padding:8px 14px;border-radius:20px;font-size:13px;border:1px solid #333}
.wrap{max-width:900px;margin:0 auto;padding:30px 20px}
h1{font-size:32px;margin-bottom:8px;background:linear-gradient(90deg,#fff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
p{color:#888;margin-bottom:20px}
.box{background:#151515;border:1px solid #222;border-radius:20px;padding:16px;display:flex;gap:10px;margin-bottom:18px}
input{flex:1;background:#0f0f0f;border:1px solid #333;color:#fff;padding:14px 16px;border-radius:14px;font-size:16px;outline:none}
button.gen{background:#fff;color:#000;border:none;padding:14px 22px;border-radius:14px;font-weight:700;cursor:pointer}
button.gen:disabled{opacity:0.5}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.chip{background:#1a1a1a;border:1px solid #2a2a2a;color:#bbb;padding:8px 12px;border-radius:20px;font-size:12px;cursor:pointer}
.chip:hover{background:#fff;color:#000}
#result{margin-top:20px}
#result img{width:100%;border-radius:18px;border:1px solid #222}
.actions{margin-top:12px;display:flex;gap:10px}
.actions a{padding:10px 16px}
#loading{color:#a78bfa;margin-top:12px;display:none}
</style></head><body>
<header><h3>companionAI 🎨</h3><div style="display:flex;gap:8px"><a href="/">💬 Chat</a><a href="/game">🎮 Game</a></div></header>
<div class="wrap">
<h1>AI Image Generator</h1>
<p>Type wetin you wan see, AI go create am for you - No API key needed!</p>
<div class="chips">
<span class="chip" onclick="setPrompt(this)">A futuristic Lagos city at night, cyberpunk</span>
<span class="chip" onclick="setPrompt(this)">African king with golden crown, royal</span>
<span class="chip" onclick="setPrompt(this)">Cute Nigerian jollof rice as anime character</span>
<span class="chip" onclick="setPrompt(this)">Barthoroyal logo, neon, premium</span>
</div>
<div class="box">
<input id="prompt" placeholder="e.g. A lion wearing agbada in space...">
<button class="gen" id="btn" onclick="generate()">Generate ✨</button>
</div>
<div id="loading">🎨 Generating your image... (5 seconds)</div>
<div id="result"></div>
</div>
<script>
function setPrompt(el){document.getElementById('prompt').value=el.innerText; generate();}
async function generate(){
 let p=document.getElementById('prompt').value.trim(); if(!p) return;
 let btn=document.getElementById('btn'); let load=document.getElementById('loading'); let res=document.getElementById('result');
 btn.disabled=true; load.style.display='block'; res.innerHTML='';
 let enc=encodeURIComponent(p);
 let url=`https://image.pollinations.ai/prompt/${enc}?width=1024&height=1024&seed=${Date.now()}&nologo=true`;
 // preload
 let img=new Image(); img.onload=()=>{ load.style.display='none'; btn.disabled=false; res.innerHTML=`<img src="${url}"><div class="actions"><a href="${url}" target="_blank" download>⬇ Download</a><a href="#" onclick="navigator.clipboard.writeText('${url}');return false;">🔗 Copy Link</a></div>`; };
 img.onerror=()=>{ load.style.display='none'; btn.disabled=false; res.innerHTML='Error generating, try again'; };
 img.src=url;
}
</script>
</body></html>"""

GAME_UI = """<!DOCTYPE html><html><head><title>Barthoroyal Shooter</title>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#000;overflow:hidden;font-family:system-ui}canvas{display:block}</style>
</head><body>
<canvas id="c"></canvas>
<script>
const canvas=document.getElementById('c'), ctx=canvas.getContext('2d');
function resize(){canvas.width=innerWidth; canvas.height=innerHeight} resize(); window.onresize=resize;
let player={x:innerWidth/2,y:innerHeight-80,w:40,h:40}, bullets=[], enemies=[], particles=[], score=0, lives=3, gameOver=false, keys={};
let enemyTimer=0;
function spawnEnemy(){ enemies.push({x:Math.random()*(canvas.width-40),y:-40,w:30+Math.random()*20,h:30,s:1+Math.random()*2+score/100,color:`hsl(${Math.random()*60+260},80%,60%)`}); }
function shoot(){ bullets.push({x:player.x,y:player.y,w:4,h:12,s:8}); }
function explode(x,y,color){ for(let i=0;i<12;i++) particles.push({x,y,vx:(Math.random()-0.5)*8,vy:(Math.random()-0.5)*8,life:20,color}); }
let lastShoot=0;
function update(){
 if(gameOver) return;
 if(keys['ArrowLeft']||keys['a']) player.x-=6;
 if(keys['ArrowRight']||keys['d']) player.x+=6;
 player.x=Math.max(0,Math.min(canvas.width-player.w,player.x));
 if((keys[' ']||keys['w']||keys['ArrowUp']) && Date.now()-lastShoot>150){ shoot(); lastShoot=Date.now(); }
 enemyTimer++; if(enemyTimer> Math.max(20,60-score/2)){ spawnEnemy(); enemyTimer=0; }
 bullets.forEach((b,i)=>{ b.y-=b.s; if(b.y<0) bullets.splice(i,1); });
 enemies.forEach((e,ei)=>{
   e.y+=e.s;
   if(e.y>canvas.height){ enemies.splice(ei,1); lives--; if(lives<=0) gameOver=true; }
   bullets.forEach((b,bi)=>{
     if(b.x<e.x+e.w && b.x+b.w>e.x && b.y<e.y+e.h && b.y+b.h>e.y){
       explode(e.x+e.w/2,e.y+e.h/2,e.color); enemies.splice(ei,1); bullets.splice(bi,1); score+=10;
     }
   });
   if(player.x<e.x+e.w && player.x+player.w>e.x && player.y<e.y+e.h && player.y+player.h>e.y){
     explode(player.x+player.w/2,player.y+player.h/2,'#fff'); enemies.splice(ei,1); lives--; if(lives<=0) gameOver=true;
   }
 });
 particles.forEach((p,i)=>{ p.x+=p.vx; p.y+=p.vy; p.life--; if(p.life<=0) particles.splice(i,1); });
}
function draw(){
 ctx.fillStyle='#070710'; ctx.fillRect(0,0,canvas.width,canvas.height);
 // stars
 ctx.fillStyle='#ffffff11'; for(let i=0;i<80;i++) ctx.fillRect((i*123)%canvas.width,(i*321+Date.now()/20)%canvas.height,2,2);
 // player
 ctx.fillStyle='#fff'; ctx.shadowColor='#8b5cf6'; ctx.shadowBlur=20; ctx.fillRect(player.x,player.y,player.w,player.h); ctx.shadowBlur=0;
 ctx.fillStyle='#8b5cf6'; ctx.fillRect(player.x+player.w/2-2,player.y-10,4,10);
 // bullets
 ctx.fillStyle='#f0f'; bullets.forEach(b=>{ ctx.fillRect(b.x,b.y,b.w,b.h); });
 // enemies
 enemies.forEach(e=>{ ctx.fillStyle=e.color; ctx.shadowColor=e.color; ctx.shadowBlur=12; ctx.fillRect(e.x,e.y,e.w,e.h); ctx.shadowBlur=0; });
 // particles
 particles.forEach(p=>{ ctx.fillStyle=p.color; ctx.globalAlpha=p.life/20; ctx.fillRect(p.x,p.y,4,4); ctx.globalAlpha=1; });
 // UI
 ctx.fillStyle='#fff'; ctx.font='18px system-ui'; ctx.fillText(`Score: ${score} | Lives: ${lives}`,14,28);
 ctx.fillStyle='#ffffff88'; ctx.font='12px system-ui'; ctx.fillText('Move: A/D or ← → | Shoot: SPACE | Tap screen to shoot',14,canvas.height-12);
 if(gameOver){ ctx.fillStyle='#000a'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#fff'; ctx.font='bold 42px system-ui'; ctx.textAlign='center'; ctx.fillText('GAME OVER',canvas.width/2,canvas.height/2-20); ctx.font='20px system-ui'; ctx.fillText(`Score: ${score}`,canvas.width/2,canvas.height/2+20); ctx.fillText('Tap or Press R to Restart',canvas.width/2,canvas.height/2+60); ctx.textAlign='left'; }
}
window.addEventListener('keydown',e=>{ keys[e.key]=true; if(e.key==='r'&&gameOver){ enemies=[]; bullets=[]; score=0; lives=3; gameOver=false; } });
window.addEventListener('keyup',e=>{ keys[e.key]=false; });
canvas.addEventListener('touchmove',e=>{ player.x=e.touches[0].clientX-player.w/2; e.preventDefault(); },{passive:false});
canvas.addEventListener('touchstart',e=>{ if(gameOver){ enemies=[]; bullets=[]; score=0; lives=3; gameOver=false; } else shoot(); },{passive:false});
(function loop(){ update(); draw(); requestAnimationFrame(loop); })();
</script>
</body></html>"""

@app.route('/')
def home(): return render_template_string(UI)

@app.route('/generate-image')
def image_page(): return render_template_string(IMAGE_UI)

@app.route('/game')
def game_page(): return render_template_string(GAME_UI)

@app.route('/ask', methods=['POST'])
def ask():
    q=request.get_json().get('q','')
    result=smart_answer(q)
    return jsonify({"a": result["text"], "image": result["image"]})

if __name__=='__main__':
    app.run(port=5000)