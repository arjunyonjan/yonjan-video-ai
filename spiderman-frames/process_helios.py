#!/usr/bin/env python3
import subprocess, re, time, os, json, glob

BASE = os.path.expanduser("~/projects/yonjan-video-ai/spiderman-frames")
HTML = os.path.join(BASE, "report_helios.html")
CACHE = os.path.join(BASE, "results_helios.json")

results = {}
if os.path.exists(CACHE):
    with open(CACHE) as f:
        results = json.load(f)

frames_dir = os.path.join(BASE, "frames")
frames = sorted(glob.glob(os.path.join(frames_dir, "frame_*.jpg")))
frame_names = [os.path.basename(f) for f in frames]
total = len(frames)
print(f"Found {total} frames to analyze")

for i, fname in enumerate(frame_names):
    if fname in results:
        print(f"[SKIP] {fname} already done")
        continue

    fpath = os.path.join(frames_dir, fname)
    num = fname.replace("frame_", "").replace(".jpg", "")
    print(f"\n[{i+1}/{total}] {fname}...", flush=True)

    start = time.time()
    try:
        r = subprocess.run(["ollama", "run", "moondream", f"describe {fpath}"],
            capture_output=True, text=True, timeout=180)
        out = r.stdout or ""
        out = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out)
        out = re.sub(r"\x1b\][0-9;]*[a-zA-Z]", "", out)
        out = re.sub(r"\x1b\[?2026[hl]", "", out)
        out = re.sub(r"\x1b\[?25[hl]", "", out)
        out = re.sub(r"\x1b\[K", "", out)
        out = re.sub(r"\[?[0-9]+[DK]", " ", out)
        out = re.sub(r"\s+", " ", out).strip()
        out = re.sub(r"^Added image.*?(?=[A-Z])", "", out).strip()
        desc = out
        ms = int((time.time() - start) * 1000)
        print(f"  OK moondream {ms}ms")
    except Exception as e:
        desc = f"ERROR: {e}"
        ms = 0
        print(f"  FAIL {e}")

    try:
        ocr = subprocess.run(["tesseract", fpath, "stdout", "-l", "eng"],
            capture_output=True, text=True, timeout=30)
        ocr_text = ocr.stdout.strip()
        if ocr_text:
            print(f"  OK OCR: {ocr_text[:60]}...")
        else:
            ocr_text = ""
    except:
        ocr_text = ""

    results[fname] = {"desc": desc, "ms": ms, "ocr": ocr_text}

    with open(CACHE, "w") as f:
        json.dump(results, f, indent=2)

    ocr_section = ""
    if ocr_text:
        ocr_section = f'''<div class="mt-3 pt-3 border-t border-white/5">
          <div class="text-xs text-green-400 font-medium uppercase tracking-wider mb-1">OCR Text</div>
          <pre class="text-xs text-gray-500 bg-black/30 rounded-lg p-2 overflow-x-auto">{ocr_text}</pre>
        </div>'''

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
        <img src="frames/{fname}" alt="Frame {num}" class="w-full rounded-xl">
      </div>
      <div class="glass rounded-2xl p-4">
        <div class="text-xs text-indigo-400 font-medium uppercase tracking-wider mb-2">Moondream</div>
        <p class="text-gray-400 text-sm leading-relaxed">{desc}</p>
        {ocr_section}
        <div class="mt-3 pt-3 border-t border-white/5 text-xs text-gray-600">
          {ms}ms on RTX 5060
        </div>
      </div>
    </div>
  </div>
'''

    if not os.path.exists(HTML):
        with open(HTML, "w") as f:
            f.write('''<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Spider-Man BND Trailer - AI Analysis</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{background:#0a0a0f;color:#e5e7eb;font-family:system-ui,sans-serif}
.glass{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);backdrop-filter:blur(12px)}
</style></head><body class="min-h-screen">
<div class="max-w-6xl mx-auto px-4 py-8">
<div class="text-center mb-16">
<h1 class="text-4xl font-bold bg-gradient-to-r from-red-500 to-blue-500 bg-clip-text text-transparent">
Spider-Man: Brand New Day</h1>
<p class="text-gray-500 mt-2">AI Analysis on RTX 5060</p>
</div>
<div id="frames"></div>
</div></body></html>''')

    with open(HTML) as f:
        html = f.read()
    html = html.replace('<div id="frames">', f'<div id="frames">{insert}')
    html = html.replace('</div>\n</div></body>', '</div></div></body>')
    with open(HTML, "w") as f:
        f.write(html)

    print(f"  HTML updated")

print(f"\nDone. {len(results)}/{total} frames analyzed.")
