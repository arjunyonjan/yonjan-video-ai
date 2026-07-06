#!/usr/bin/env python3
import subprocess, re, time, os, json, glob

BASE = os.path.expanduser("~/projects/ai-vision/spiderman-frames")
HTML = os.path.join(BASE, "report.html")
CACHE = os.path.join(BASE, "results.json")

# Load existing results
results = {}
if os.path.exists(CACHE):
    with open(CACHE) as f:
        results = json.load(f)

frames = sorted(glob.glob(os.path.join(BASE, "frame_*.jpg")))
frame_names = [os.path.basename(f) for f in frames]

for fname in frame_names:
    if fname in results:
        print(f"[SKIP] {fname} already done")
        continue
    
    fpath = os.path.join(BASE, fname)
    num = fname.replace("frame_", "").replace(".jpg", "")
    print(f"\n[{num}/{len(frames)}] {fname}...", flush=True)
    
    # Moondream
    start = time.time()
    try:
        r = subprocess.run(["ollama", "run", "moondream", f"describe {fpath}"],
            capture_output=True, text=True, timeout=180)
        out = r.stdout or ""
        out = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', out)
        out = re.sub(r'\x1b\][0-9;]*[a-zA-Z]', '', out)
        out = re.sub(r'\x1b\[?2026[hl]', '', out)
        out = re.sub(r'\x1b\[?25[hl]', '', out)
        out = re.sub(r'\x1b\[K', '', out)
        out = re.sub(r'\[?[0-9]+[DK]', ' ', out)
        out = re.sub(r'\s+', ' ', out).strip()
        out = re.sub(r'^Added image.*?(?=[A-Z])', '', out).strip()
        desc = out
        ms = int((time.time() - start) * 1000)
        print(f"  ✓ moondream {ms}ms")
    except Exception as e:
        desc = f"ERROR: {e}"
        ms = 0
        print(f"  ✗ {e}")
    
    # OCR
    try:
        ocr = subprocess.run(["tesseract", fpath, "stdout", "-l", "eng"],
            capture_output=True, text=True, timeout=30)
        ocr_text = ocr.stdout.strip()
        if ocr_text:
            print(f"  ✓ OCR: {ocr_text[:60]}...")
        else:
            ocr_text = ""
    except:
        ocr_text = ""
    
    results[fname] = {"desc": desc, "ms": ms, "ocr": ocr_text}
    
    with open(CACHE, "w") as f:
        json.dump(results, f, indent=2)
    
    # Update HTML
    insert = f'''
  <div class="mb-12">
    <div class="flex items-center gap-3 mb-4">
      <div class="h-px flex-1 bg-white/5"></div>
      <span class="text-xs font-semibold text-gray-500 tracking-widest uppercase">Frame {num}</span>
      <span class="text-xs text-gray-600">{ms/1000:.1f}s</span>
      <div class="h-px flex-1 bg-white/5"></div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="glass rounded-2xl p-3">
        <img src="{fname}" alt="Frame {num}" class="w-full rounded-xl">
      </div>
      <div class="glass rounded-2xl p-4">
        <div class="text-xs text-indigo-400 font-medium uppercase tracking-wider mb-2">Moondream</div>
        <p class="text-gray-400 text-sm leading-relaxed">{desc}</p>
        {"".join(f'''
        <div class="mt-3 pt-3 border-t border-white/5">
          <div class="text-xs text-green-400 font-medium uppercase tracking-wider mb-1">OCR Text</div>
          <pre class="text-xs text-gray-500 bg-black/30 rounded-lg p-2 overflow-x-auto">{ocr_text}</pre>
        </div>''' if ocr_text else "")}
        <div class="mt-3 pt-3 border-t border-white/5 text-xs text-gray-600">
          ⏱ {ms}ms on Honor 90 · RTX 3060 est: {int(ms*0.07)}ms · RTX 5060 est: {int(ms*0.035)}ms
        </div>
      </div>
    </div>
  </div>
'''
    with open(HTML) as f:
        html = f.read()
    html = html.replace('<div id="frames"></div>',
        f'<div id="frames">{insert}</div>')
    with open(HTML, "w") as f:
        f.write(html)
    
    print(f"  → HTML updated")

print(f"\n✅ Done. {len(results)}/{len(frames)} frames analyzed.")
print(f"Open: file://{HTML}")
