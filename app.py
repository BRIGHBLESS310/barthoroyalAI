from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os, re, math

app = Flask(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0"}

def free_ai_answer(q):
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(q)}?model=openai"
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and len(r.text) > 5:
            return r.text
        return None
    except:
        return None

def smart_answer(q):
    if not q: return {"text": "Ask me anything!", "image": None}
    low = q.lower()
    if any(k in low for k in ["image", "draw", "picture", "imagine"]):
        safe = urllib.parse.quote(q)
        img = f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&seed={abs(hash(q))%1000}"
        return {"text": f"Image for: {q}", "image": img}
    ans = free_ai_answer(q)
    if ans:
        return {"text": ans, "image": None}
    return {"text": f"I fit answer: {q} - try again, my free brain dey load!", "image": None}

UI = """<!DOCTYPE html><html><head><title>cAI</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#0a0a0a;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}#chat{flex:1;overflow:auto;padding:20px;max-width:760px;margin:0 auto;width:100%}.b{padding:12px;border-radius:18px;margin:8px 0;white-space:pre-wrap}.u{margin-left:auto;background:#fff;color:#000}.ai{background:#1a1a1a}input{flex:1;background:#222;color:#fff;border:none;padding:12px;border-radius:20px}footer{padding:12px;display:flex;gap:8px;max-width:760px;margin:0 auto;width:100%}button{background:#fff;color:#000;border:none;padding:10px 16px;border-radius:20px}</style></head><body><div id="chat"></div><footer><input id="i" placeholder="Ask anything JSS2 math..." onkeydown="if(event.key==='Enter')go()"><button onclick="go()">Send</button></footer><script>async function go(){let inp=document.getElementById('i');let q=inp.value;if(!q)return;let c=document.getElementById('chat');c.innerHTML+=`<div class=b u>${q}</div>`;inp.value='';c.innerHTML+=`<div class=b ai id=t>Thinking...</div>`;let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q})}).then(r=>r.json());document.getElementById('t').remove();c.innerHTML+=`<div class=b ai>${r.a}${r.image?`<br><img src=${r.image} style='width:100%;border-radius:12px;margin-top:10px'>`:''}</div>`;c.scrollTop=9999;}</script></body></html>"""

@app.route('/')
def home(): return render_template_string(UI)
@app.route('/logo.png')
def logo():
    try: return send_from_directory('.', 'logo.png')
    except: return "",404
@app.route('/ask', methods=['POST'])
def ask():
    q = request.get_json().get('q','')
    return jsonify({"a": smart_answer(q)["text"], "image": smart_answer(q)["image"]})

if __name__ == '__main__': app.run()