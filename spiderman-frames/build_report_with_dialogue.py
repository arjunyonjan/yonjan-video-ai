#!/usr/bin/env python3
import json, re, os

BASE = os.path.expanduser("~/projects/yonjan-video-ai/spiderman-frames")
RESULTS = os.path.join(BASE, "results_helios.json")
TRANSCRIPT = os.path.join(BASE, "transcript_helios.txt")
OUTPUT = os.path.join(BASE, "report_helios.html")

with open(RESULTS) as f:
    results = json.load(f)

segments = []
with open(TRANSCRIPT) as f:
    for line in f:
        m = re.match(r'\[(\d+\.?\d*)s -> (\d+\.?\d*)s\] (.+)', line)
        if m:
            segments.append((float(m.group(1)), float(m.group(2)), m.group(3)))

def get_dialogue(frame_sec):
    frame_sec = int(frame_sec)
    matching = []
    for start, end, text in segments:
        if start <= frame_sec + 0.5 and end >= frame_sec - 0.5:
            matching.append(text)
    return matching

frames_html = ""
frame_names = sorted(results.keys(), key=lambda x: int(re.sub(r'\D', '', x)))

for fname in frame_names:
    r = results[fname]
    num = fname.replace("frame_", "").replace(".jpg", "")
    sec = int(num)
    desc = r["desc"]
    ms = r["ms"]
    ocr_text = r.get("ocr", "")
    dialogue = get_dialogue(sec)

    ocr_section = ""
    if ocr_text:
        ocr_section = f'''<div class="mt-3 pt-3 border-t border-white/5">
          <div class="text-xs text-green-400 font-medium uppercase tracking-wider mb-1">OCR Text</div>
          <pre class="text-xs text-gray-500 bg-black/30 rounded-lg p-2 overflow-x-auto">{ocr_text}</pre>
        </div>'''

    dialogue_section = ""
    if dialogue:
        lines = "".join(f'<span class="block text-yellow-300/80 text-sm italic">"{d}"</span>' for d in dialogue)
        dialogue_section = f'''<div class="mt-3 pt-3 border-t border-white/5">
          <div class="text-xs text-yellow-400 font-medium uppercase tracking-wider mb-1">Dialogue</div>
          <div class="space-y-1">{lines}</div>
        </div>'''

    frames_html += f'''
  <div class="mb-12">
    <div class="flex items-center gap-3 mb-4">
      <div class="h-px flex-1 bg-white/5"></div>
      <span data-seek="{num}" class="text-xs font-semibold text-gray-500 tracking-widest uppercase cursor-pointer hover:text-indigo-400 transition">Frame {num}s</span>
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
        {dialogue_section}
        {ocr_section}
        <div class="mt-3 pt-3 border-t border-white/5 text-xs text-gray-600">
          {ms}ms on RTX 5060
        </div>
      </div>
    </div>
  </div>'''

yt_id = "62bIsvRcPv0"
html = f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Spider-Man BND Trailer - AI Analysis</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:#0a0a0f;color:#e5e7eb;font-family:system-ui,sans-serif}}
.glass{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);backdrop-filter:blur(12px)}}
</style></head><body class="min-h-screen">
<div class="max-w-7xl mx-auto px-4 py-8">
<div class="text-center mb-8">
<h1 class="text-4xl font-bold bg-gradient-to-r from-red-500 to-blue-500 bg-clip-text text-transparent">
Spider-Man: Brand New Day</h1>
<p class="text-gray-500 mt-2">AI Analysis on RTX 5060</p>
<p class="text-gray-600 text-sm mt-1">162 frames · Moondream vision · Tesseract OCR · Whisper STT</p>
</div>
<div class="flex flex-col lg:flex-row gap-6">
  <div id="trailer-col" class="w-full lg:w-[480px] shrink-0">
    <div class="sticky top-4 z-10">
      <div class="flex gap-2 mb-2">
        <button id="toggle-trailer-btn" class="text-xs text-gray-400 bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full flex-1 transition flex items-center justify-center gap-1.5" onclick="var v=document.getElementById('trailer-video'),b=this;v.classList.toggle('hidden');b.innerHTML=v.classList.contains('hidden')?'<svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" class=\"inline-block\"><circle cx=\"12\" cy=\"12\" r=\"10\"/><polygon points=\"10,8 16,12 10,16\" fill=\"currentColor\" stroke=\"none\"/></svg> Show':'<svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" class=\"inline-block\"><circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2\"/></svg> Hide';"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="inline-block"><circle cx="12" cy="12" r="10"/><path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"/></svg> Hide</button>
      </div>
      <div id="trailer-video" class="relative w-full" style="padding-bottom:56.25%">
        <iframe id="yt-player" class="absolute top-0 left-0 w-full h-full rounded-2xl overflow-hidden glass" src="https://www.youtube.com/embed/{yt_id}?enablejsapi=1&rel=0" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
      </div>
    </div>
  </div>
  <div class="flex-1 min-w-0">
    <div id="frames">''' + frames_html + '''</div>
  </div>
</div>
</div>
<script>
document.querySelectorAll('[data-seek]').forEach(el => {
  el.addEventListener('click', () => {
    const t = parseInt(el.dataset.seek);
    const iframe = document.getElementById('yt-player');
    iframe.src = iframe.src.replace(/[?&]start=\d+/,'') + '&start=' + t;
  });
});
</script>
</body></html>'''

with open(OUTPUT, "w") as f:
    f.write(html)

print(f"Written {OUTPUT} with {len(frame_names)} frames and dialogue overlay")
