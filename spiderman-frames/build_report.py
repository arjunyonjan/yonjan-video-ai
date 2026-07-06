#!/usr/bin/env python3
import json, os, re

BASE = os.path.expanduser("~/projects/ai-vision/spiderman-frames")

with open(os.path.join(BASE, "results.json")) as f:
    results = json.load(f)

with open(os.path.join(BASE, "transcript.txt")) as f:
    raw_lines = f.readlines()

# Parse transcript: [00:00:05.000 --> 00:00:10.000] Text...
transcript = []
for line in raw_lines:
    line = line.strip()
    m = re.match(r'\[(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\]\s*(.*)', line)
    if m:
        start_ts = m.group(1)
        end_ts = m.group(2)
        text = m.group(3).strip()
        # Convert to seconds for matching
        parts = start_ts.split(':')
        sec = int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
        transcript.append({"start": start_ts, "end": end_ts, "text": text, "sec": sec})

def get_dialogue(frame_num):
    """Get dialogue closest to this frame's timestamp (frame_num * 5 seconds)"""
    frame_sec = int(frame_num) * 5
    matching = []
    for t in transcript:
        if t["sec"] - 2 <= frame_sec <= t["sec"] + 3:
            matching.append(t["text"])
    return matching

sections = []
for fname in sorted(results.keys()):
    r = results[fname]
    num = fname.replace("scene_","").replace("frame_","").replace(".jpg","")
    frame_sec = int(num) * 5
    ts = f"{frame_sec//60}:{frame_sec%60:02d}"
    desc = r['desc']
    ms = r['ms']
    ocr = r.get('ocr','')
    
    dialogue = get_dialogue(num)
    dialogue_html = ""
    if dialogue:
        dlines = "<br>".join(dialogue)
        dialogue_html = f'<div class="mt-2 pt-2 border-t border-white/5"><div class="text-xs text-yellow-400 font-medium uppercase tracking-wider mb-1">Dialogue</div><div class="text-xs text-yellow-300/80 leading-relaxed">{dlines}</div></div>'
    
    ocr_html = ""
    if ocr:
        ocr_html = f'<div class="mt-2 pt-2 border-t border-white/5"><div class="text-xs text-green-400 font-medium uppercase tracking-wider mb-1">OCR Text</div><pre class="text-xs text-gray-500 bg-black/30 rounded-lg p-2 overflow-x-auto">{ocr}</pre></div>'
    
    section = f'''
  <div class="mb-8" id="frame-{num}">
    <div class="flex items-center gap-3 mb-3">
      <div class="h-px flex-1 bg-white/5"></div>
      <span class="text-xs font-semibold text-gray-500 tracking-widest uppercase">Frame {num} · {ts}</span>
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
        {dialogue_html}
        {ocr_html}
        <div class="mt-2 pt-2 border-t border-white/5 text-xs text-gray-600">
          ⏱ {ms}ms · RTX 3060 est: {int(ms*0.07)}ms · RTX 5060 est: {int(ms*0.035)}ms
        </div>
      </div>
    </div>
  </div>'''
    sections.append(section)

all_frames_html = "\n".join(sections)
total = len(results)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Spider-Man: Brand New Day — Frame Analysis</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{font-family:Inter,sans-serif;background:#0a0a0f;color:#e5e7eb;padding-top:220px;transition:padding-top 0.3s}}
body.video-hidden{{padding-top:40px}}
.glass{{background:rgba(255,255,255,0.03);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.06)}}
#video-bar{{position:fixed;top:0;left:0;right:0;z-index:50;background:#030712;border-bottom:1px solid rgba(255,255,255,0.06);padding:8px 16px;transition:transform 0.3s}}
#video-bar.hidden{{transform:translateY(-100%)}}
#video-bar iframe{{width:100%;max-width:400px;height:160px;margin:0 auto;display:block;border-radius:10px}}
#video-toggle{{position:fixed;top:4px;right:12px;z-index:51;cursor:pointer;color:#6b7280;font-size:12px;padding:4px 8px;border-radius:4px;background:rgba(3,7,18,0.8);border:1px solid rgba(255,255,255,0.06)}}
</style>
</head>
<body>
<div id="video-toggle" onclick="toggleVideo()">&#9650; Hide</div>
<div id="video-bar">
  <iframe src="https://www.youtube.com/embed/62bIsvRcPv0?autoplay=0&rel=0" frameborder="0" allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope" allowfullscreen></iframe>
  <div class="text-center mt-1">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-medium">
      <span class="w-2 h-2 rounded-full bg-red-400 animate-pulse"></span>
      Spider-Man: Brand New Day &#183; Scene Detect &#183; {total}/43 scenes
    </div>
  </div>
</div>
<script>
function toggleVideo(){{
  var bar = document.getElementById('video-bar');
  var btn = document.getElementById('video-toggle');
  var body = document.body;
  if (bar.classList.contains('hidden')) {{
    bar.classList.remove('hidden');
    body.classList.remove('video-hidden');
    btn.innerHTML = '&#9650; Hide';
  }} else {{
    bar.classList.add('hidden');
    body.classList.add('video-hidden');
    btn.innerHTML = '&#9660; Show';
  }}
}}</script>

<div class="max-w-5xl mx-auto">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-extrabold"><span class="bg-gradient-to-r from-red-500 via-blue-500 to-red-500 bg-clip-text text-transparent">Frame Analysis</span></h1>
    <p class="text-gray-600 mt-1 text-xs">Moondream + Whisper STT + Tesseract OCR · Scene detect · Honor 90</p>
  </div>
  {all_frames_html}
  <div class="text-center pt-8 pb-8">
    <p class="text-xs text-gray-700">Generated 2026-07-06 · Moondream via Ollama</p>
  </div>
</div>
</body>
</html>'''

with open(os.path.join(BASE, "report.html"), "w") as f:
    f.write(html)
print(f"Report generated with {total} frames, {len(transcript)} transcript lines")
