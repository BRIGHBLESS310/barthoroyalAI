from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, urllib.parse, os, re, math

app = Flask(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0"}

def solve_math(q):
    try:
        low = q.lower()
        if "square root" in low:
            nums = re.findall(r'\d+', low)
            if nums:
                n = float(nums[-1])
                r = math.sqrt(n)
                if r == int(r): r = int(r)
                return f"Answer: Square root of {int(n)} = {r} (because {r} x {r} = {int(n)})"
        text = low.replace("divided by", "/").replace("divide by", "/").replace("divided", "/")
        text = text.replace("multiplied by", "*").replace("times", "*").replace("x", "*")
        text = text.replace("plus", "+").replace("minus", "-")
        pattern = r'(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)'
        matches = re.findall(pattern, text)
        if matches:
            for a, op, b in matches:
                try:
                    a_f = float(a); b_f = float(b)
                    if op == '+': res = a_f + b_f
                    elif op == '-': res = a_f - b_f
                    elif op == '*': res = a_f * b_f
                    elif op == '/':
                        if b_f == 0: continue
                        res = a_f / b_f
                    if res == int(res): res = int(res)
                    return f"Answer: {a} {op} {b} = {res}"
                except: continue
        return None
    except: return None

def wiki_answer(q):
    try:
        low = q.lower()
        if "human cell" in low or "parts of cell" in low:
            return "Human Cell Parts:\n\n1. Nucleus - controls cell activities and contains DNA\n2. Cell Membrane - outer covering that protects cell\n3. Cytoplasm - jelly-like fluid inside cell\n4. Mitochondria - powerhouse, produces energy\n5. Ribosomes - makes protein\n6. Endoplasmic Reticulum - transports materials\n7. Golgi Apparatus - packages proteins\n8. Vacuole - storage\n9. Lysosome - digests waste\n10. Chloroplast (plant cell) - for photosynthesis\n\nSource: Biology"
        if "photosynthesis" in low:
            return "Photosynthesis:\n\nProcess where green plants use sunlight to make food.\n\nEquation: CO2 + Water + Sunlight = Glucose + Oxygen\n\nOccurs in chloroplast, needs chlorophyll.\n\nImportance: Produces oxygen we breathe and food for plants."
        if "teach me python" in low or "python programming" in low or "learn python" in low or low.strip() == "python":
            return "Python Programming for Beginners:\n\n1. Print:\nprint('Hello World')\n\n2. Variables:\nname = 'John'\nage = 20\n\n3. Calculation:\nx = 10\ny = 20\nprint(x + y) # 30\n\n4. Input:\nname = input('Enter your name: ')\nprint('Hello ' + name)\n\n5. If Statement:\nage = 20\nif age >= 18:\n print('Adult')\nelse:\n print('Young')\n\n6. Loop:\nfor i in range(5):\n print(i)\n\nTry: Write a calculator in Python"
        if "longest river" in low:
            return "Longest River in the World:\n\n1. Nile River - 6,650 km - Africa, flows through Egypt, Sudan\n2. Amazon River - 6,400 km - South America\n3. Yangtze River - 6,300 km - China\n\nNile is officially longest."
        if "richest man" in low or "richest person" in low:
            return "Richest Man in World (2026):\n\n1. Elon Musk - Tesla, SpaceX - $400B+\n2. Jeff Bezos - Amazon\n3. Bernard Arnault - LVMH\n4. Mark Zuckerberg - Meta\n\nNet worth changes daily with stock market."
        if "capital of nigeria" in low:
            return "Capital of Nigeria is Abuja. Largest city is Lagos. Abuja became capital in 1991."

        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json"
        r = requests.get(url, headers=HEADERS, timeout=8)
        data = r.json()
        if data.get('query',{}).get('search'):
            title = data['query']['search'][0]['title']
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
            r2 = requests.get(summary_url, headers=HEADERS, timeout=8)
            if r2.status_code == 200:
                d2 = r2.json()
                extract = d2.get('extract', '')
                if len(extract) > 20:
                    return f"{title}:\n\n{extract}\n\nSource: Wikipedia"
        return None
    except: return None

def smart_answer(q):
    low = q.lower().strip()
    if not q: return {"text": "Ask me anything!", "image": None}
    if any(k in low for k in ["generate image", "create image", "make image", "draw", "image of", "picture of", "imagine"]):
        prompt = q
        for k in ["generate image of", "generate image", "create image", "image of", "picture of", "imagine", "draw"]:
            if k in low:
                prompt = q.lower().split(k, 1)[-1].strip()
                break
        safe_prompt = urllib.parse.quote(prompt if len(prompt)>2 else q)
        img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed={abs(hash(q))%100000}&nologo=true"
        return {"text": f"Created image: {prompt}", "image": img_url}
    math_res = solve_math(q)
    if math_res:
        return {"text": math_res, "image": None}
    wiki = wiki_answer(q)
    if wiki:
        return {"text": wiki, "image": None}
    return {"text": f"For '{q}': I can answer Maths, Biology, Rivers, People, Coding. Try: 'What is photosynthesis?', '144 divided by 12', 'longest river'", "image": None}

UI = """<!DOCTYPE html><html><head><title>cAI School AI</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}body{background:#0a0a0a;color:#ececec;height:100vh;display:flex;flex-direction:column}#loader{position:fixed;inset:0;background:#050505;display:flex;align-items:center;justify-content:center;z-index:9999;transition:opacity.6s}#loader.hide{opacity:0;pointer-events:none}.logo-load{width:180px;height:180px;animation:spin 2.5s linear infinite}@keyframes spin{0%{transform:rotateY(0)}100%{transform:rotateY(360deg)}}header{padding:12px 16px;display:flex;justify-content:space-between;border-bottom:1px solid #1a1a1a}#chat{flex:1;overflow:auto;padding:20px;max-width:760px;margin:0 auto;width:100%;display:flex;flex-direction:column}.bubble{padding:12px 16px;border-radius:20px;max-width:85%;margin:8px 0;white-space:pre-wrap;font-size:14px;line-height:1.6}.user{margin-left:auto;background:#fff;color:#000;border-bottom-right-radius:6px}.bot{background:#161616;border:1px solid #232323}.bot img{width:100%;max-width:400px;border-radius:12px;margin-top:10px}footer{border-top:1px solid #1a1a1a;padding:14px;display:flex;justify-content:center}.box{width:100%;max-width:760px;background:#181818;border:1px solid #2a2a2a;border-radius:24px;display:flex;align-items:center;padding:4px 6px 4px 14px}input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:10px;font-size:15px}button.send{background:#fff;color:#000;border:none;width:32px;height:32px;border-radius:50%;cursor:pointer;font-weight:900}.btn{color:#555;font-size:11px;border:1px solid #222;padding:5px 12px;border-radius:16px;background:transparent;cursor:pointer}</style></head><body><div id="loader"><img src="/logo.png" class="logo-load" onerror="this.style.display='none'"></div><header><b style="color:gold">cAI School AI</b><button class="btn" onclick="localStorage.clear();document.getElementById('chat').innerHTML='';location.reload()">New Chat</button></header><div id="chat"></div><footer><div class="box"><input id="inp" placeholder="Ask anything - Maths, Biology, Coding..." onkeydown="if(event.key==='Enter')send()"><button class="send" onclick="send()">^</button></div></footer><script>window.onload=()=>{setTimeout(()=>document.getElementById('loader').classList.add('hide'),1500);let s=localStorage.getItem('cAI_final_v3');if(s)document.getElementById('chat').innerHTML=s;else document.getElementById('chat').innerHTML='<div style="text-align:center;margin-top:80px"><h2>Good morning</h2><p style="color:#888;margin-top:10px">Ask: Maths, Biology, longest river, richest man, Python</p></div>';};async function send(){let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;let c=document.getElementById('chat');c.innerHTML+='<div class="bubble user">'+t+'</div>';i.value='';c.innerHTML+='<div class="bubble bot" id="tmp">Thinking...</div>';c.scrollTop=99999;let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})}).then(r=>r.json());document.getElementById('tmp')?.remove();let img=r.image?'<img src="'+r.image+'">':'';c.innerHTML+='<div class="bubble bot">'+r.a+img+'</div>';c.scrollTop=99999;localStorage.setItem('cAI_final_v3',c.innerHTML);}</script></body></html>
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
if __name__=='__main__': app.run(port=5000)