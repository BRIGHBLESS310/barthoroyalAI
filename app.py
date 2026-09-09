from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os

app = Flask(__name__)

def get_answer(q):
    # BRAIN 1: Pollinations OpenAI format (strongest free)
    try:
        url = "https://gen.pollinations.ai/v1/chat/completions"
        data = {
            "model": "openai",
            "messages": [{"role": "user", "content": f"You are cAI School AI for Nigerian JSS2. Explain simply: {q}"}],
            "max_tokens": 800
        }
        r = requests.post(url, json=data, timeout=25)
        if r.status_code == 200:
            j = r.json()
            ans = j['choices'][0]['message']['content']
            if len(ans) > 10:
                return ans
    except Exception as e:
        print("Brain1 fail:", e)

    # BRAIN 2: Simple pollinations GET
    try:
        url2 = f"https://text.pollinations.ai/{urllib.parse.quote(q)}"
        r2 = requests.get(url2, timeout=15)
        if r2.status_code == 200 and len(r2.text) > 10:
            return r2.text
    except:
        pass

    # BRAIN 3: Wikipedia backup
    try:
        wurl = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(q)}"
        rw = requests.get(wurl, timeout=10)
        if rw.status_code == 200:
            return rw.json().get('extract', None)
    except:
        pass

    return None

def smart(q):
    if not q:
        return {"text": "Ask me!", "image": None}
    if any(x in q.lower() for x in ["image", "draw", "picture"]):
        img = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(q)}?nologo=true&width=1024&height=1024"
        return {"text": f"Image: {q}", "image": img}

    ans = get_answer(q)
    if ans:
        return {"text": ans, "image": None}

    # If all fail, give local answer for common questions
    low = q.lower()
    if "computer" in low:
        return {"text": """**What is a Computer for JSS2?**

A Computer is an electronic machine that can accept data, process data, store data and give out information.

**Types of Computer:**
1. Super Computer - very fast, for weather
2. Mainframe - big companies
3. Mini Computer - medium
4. Micro Computer - Desktop, Laptop, Phone

**Uses of Computer:**
1. In Schools - for teaching and learning
2. In Banks - to keep money records
3. In Hospitals - to check patients
4. For Communication - WhatsApp, Facebook
5. For Games and Entertainment
6. For Business - typing and calculation

**Parts of Computer:**
- Hardware: Keyboard, Mouse, Monitor
- Software: Windows, Apps

Computer makes work faster and easier!""", "image": None}

    return {"text": f"I dey try connect to free brain for '{q}'. Please wait 10 secs and try again! Network slow small.", "image": None}

UI = """<!DOCTYPE html><html><head><title>cAI School</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#000;color:#fff;font-family:sans-serif;margin:0;height:100vh;display:flex;flex-direction:column}#chat{flex:1;overflow:auto;padding:20px;max-width:800px;margin:auto;width:100%}.b{padding:14px;border-radius:16px;margin:10px 0;white-space:pre-wrap;line-height:1.6}.u{background:#fff;color:#000;margin-left:auto}.ai{background:#1e1e1e;border:1px solid #333}footer{padding:15px;display:flex;gap:10px;max-width:800px;margin:auto;width:100%}input{flex:1;padding:12px;border-radius:25px;border:1px solid #333;background:#111;color:#fff}button{padding:12px 20px;border-radius:25px;border:none;background:#fff;color:#000;font-weight:bold}</style></head><body><div id="chat"><div class=b ai>👋 I am cAI School AI! Ask me anything about JSS2 Computer, Maths, Science!</div></div><footer><input id="q" placeholder="What is computer and its uses for JSS2?" onkeydown="if(event.key==='Enter')go()"><button onclick="go()">Send</button></footer><script>async function go(){let i=document.getElementById('q');let t=i.value;if(!t)return;let c=document.getElementById('chat');c.innerHTML+=`<div class=b u>${t}</div>`;i.value='';c.innerHTML+=`<div class=b ai id=load>🧠 Thinking...</div>`;c.scrollTop=99999;try{let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(x=>x.json());document.getElementById('load').remove();c.innerHTML+=`<div class=b ai>${r.a}${r.image?`<br><img src='${r.image}' style='width:100%;border-radius:12px;margin-top:10px'>`:''}</div>`;}catch(e){document.getElementById('load').innerHTML='Network error, try again!'}c.scrollTop=99999;}</script></body></html>"""

@app.route('/')
def h(): return render_template_string(UI)
@app.route('/logo.png')
def l():
    try: return send_from_directory('.', 'logo.png')
    except: return "",404
@app.route('/ask', methods=['POST'])
def ask():
    q = request.get_json().get('q','')
    res = smart(q)
    return jsonify({"a": res["text"], "image": res["image"]})

if __name__ == '__main__': app.run()