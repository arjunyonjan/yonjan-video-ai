#!/usr/bin/env python3
import subprocess, os, json, re, shutil, time
from pathlib import Path
import concurrent.futures

BASE = os.path.expanduser("~/projects/yonjan-video-ai/spiderman-frames")
VIDEO = os.path.join(BASE, "spiderman-bnd-720p.mp4")
FRAMES_DIR = os.path.join(BASE, "frames")
CLIPS_DIR = os.path.join(BASE, "scene_clips")
TRANSCRIPT = os.path.join(BASE, "transcript_helios.txt")
RESULTS_FILE = os.path.join(BASE, "results_helios.json")
STORYBOARD = os.path.join(BASE, "storyboard.html")
META = os.path.join(BASE, "scene_meta.json")
os.makedirs(CLIPS_DIR, exist_ok=True)

# Load results
with open(RESULTS_FILE) as f:
    results = json.load(f)

# Load transcript
segments = []
if os.path.exists(TRANSCRIPT):
    with open(TRANSCRIPT) as f:
        for line in f:
            m = re.match(r'\[(\d+\.?\d*)s -> (\d+\.?\d*)s\] (.+)', line)
            if m:
                segments.append((float(m.group(1)), float(m.group(2)), m.group(3)))

# Step 1: Detect scene timestamps
print("[Agent 1] Detecting scenes...")
t1 = time.time()
result = subprocess.run(
    ["ffmpeg", "-i", VIDEO, "-vf", "select=gt(scene\\,0.3),showinfo", "-vsync", "0", "-f", "null", "-"],
    capture_output=True, timeout=60
)
stderr = result.stderr.decode()
timestamps = []
for line in stderr.split('\n'):
    m = re.search(r'pts_time:([0-9.]+)', line)
    if m:
        timestamps.append(float(m.group(1)))
print(f"  Found {len(timestamps)} scene changes in {time.time()-t1:.1f}s")

# Build scene ranges
scenes = []
prev = 0.0
for t in timestamps:
    scenes.append({"num": len(scenes)+1, "start": prev, "end": t})
    prev = t
scenes.append({"num": len(scenes)+1, "start": prev, "end": 162.0})
print(f"  Total scenes: {len(scenes)}")

# Step 2: Extract ALL scene clips in parallel
print("[Agent 2] Extracting all scene clips (parallel)...")
t2 = time.time()

def extract_scene(s):
    out = os.path.join(CLIPS_DIR, f"scene_{s['num']:03d}.mp4")
    if os.path.exists(out):
        return f"  Scene {s['num']}: already exists"
    dur = s['end'] - s['start']
    subprocess.run(
        ["ffmpeg", "-ss", str(s['start']), "-i", VIDEO, "-to", str(dur),
         "-c", "copy", "-avoid_negative_ts", "make_zero", "-y", out],
        capture_output=True, timeout=120
    )
    return f"  Scene {s['num']}: {s['start']:.1f}s-{s['end']:.1f}s ({dur:.1f}s)"

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for msg in ex.map(extract_scene, scenes):
        print(msg)
print(f"  Extracted in {time.time()-t2:.1f}s")

# Step 3: Get first frame of each scene + Moondream analysis
print("[Agent 3] Analyzing first frame of each scene with Moondream...")
t3 = time.time()
scene_analysis = []

def analyze_scene(s):
    num = s['num']
    sec = int(s['start']) + 1
    fname = f"frame_{sec:03d}.jpg"
    fpath = os.path.join(FRAMES_DIR, fname)

    desc = ""
    ocr_text = ""
    dialogue = []
    ms = 0

    # Get Moondream from existing results
    if fname in results:
        desc = results[fname]["desc"]
        ms = results[fname]["ms"]
        ocr_text = results[fname].get("ocr", "")
    else:
        # Try nearest frame
        for offset in range(0, 5):
            alt = f"frame_{sec + offset:03d}.jpg"
            if alt in results:
                desc = results[alt]["desc"]
                ms = results[alt]["ms"]
                ocr_text = results[alt].get("ocr", "")
                break

    # Match dialogue to scene
    for start, end, text in segments:
        if start >= s['start'] and end <= s['end']:
            dialogue.append(text)

    return {"num": num, "start": s['start'], "end": s['end'], "duration": s['end']-s['start'],
            "first_frame": fname, "desc": desc[:200]+"..." if len(desc)>200 else desc,
            "ms": ms, "ocr": ocr_text, "dialogue": dialogue}

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    scene_analysis = list(ex.map(analyze_scene, scenes))
print(f"  Analyzed {len(scene_analysis)} scenes in {time.time()-t3:.1f}s")

# Step 4: Build storyboard HTML
print("[Agent 4] Building storyboard HTML...")
t4 = time.time()

scene_cards = ""
for s in scene_analysis:
    dialogue_html = ""
    if s["dialogue"]:
        dialogue_html = ''.join(f'<span class="block text-yellow-300/80 text-xs italic">"{d}"</span>' for d in s["dialogue"])

    frames_in_scene = []
    for sec in range(int(s['start']), int(s['end']) + 1):
        fname = f"frame_{sec:03d}.jpg"
        if os.path.exists(os.path.join(FRAMES_DIR, fname)):
            frames_in_scene.append(fname)

    scene_cards += f'''
    <div class="mb-8 scene-card" id="scene-{s['num']}">
        <div class="flex items-center gap-3 mb-3">
            <div class="h-px flex-1 bg-white/5"></div>
            <span class="text-xs font-semibold text-gray-500 tracking-widest uppercase">Scene {s['num']}</span>
            <span class="text-xs text-gray-600">{s['start']:.1f}s - {s['end']:.1f}s ({s['duration']:.1f}s)</span>
            <div class="h-px flex-1 bg-white/5"></div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="glass rounded-2xl p-3">
                <video id="scene-video-{s['num']}" class="w-full rounded-xl" controls preload="metadata">
                    <source src="scene_clips/scene_{s['num']:03d}.mp4" type="video/mp4">
                </video>
                <div class="flex flex-wrap gap-1 mt-2">
                    {''.join(f'<img src="frames/{fm}" class="w-12 h-8 object-cover rounded cursor-pointer hover:ring-2 hover:ring-indigo-400 opacity-60 hover:opacity-100 transition" onclick="document.getElementById(\'scene-video-{s["num"]}\').currentTime={int(fm.replace("frame_","").replace(".jpg","")) - s["start"]:.1f}">' for fm in frames_in_scene[:8])}
                    {f'<span class="text-xs text-gray-600 flex items-center">+{len(frames_in_scene)-8} more</span>' if len(frames_in_scene) > 8 else ''}
                </div>
            </div>
            <div class="glass rounded-2xl p-4">
                <div class="text-xs text-indigo-400 font-medium uppercase tracking-wider mb-2">Moondream</div>
                <p class="text-gray-400 text-sm leading-relaxed">{s['desc']}</p>
                {f'<div class="mt-3 pt-3 border-t border-white/5"><div class="text-xs text-yellow-400 font-medium uppercase tracking-wider mb-1">Dialogue</div><div class="space-y-1">{dialogue_html}</div></div>' if dialogue_html else ''}
                {f'<div class="mt-3 pt-3 border-t border-white/5"><div class="text-xs text-green-400 font-medium uppercase tracking-wider mb-1">OCR</div><pre class="text-xs text-gray-500 bg-black/30 rounded-lg p-2 overflow-x-auto">{s["ocr"]}</pre></div>' if s["ocr"] else ''}
                <div class="mt-3 text-xs text-gray-600">{s["ms"]}ms on RTX 5060</div>
            </div>
        </div>
    </div>'''

html = f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Spider-Man BND - Storyboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:#0a0a0f;color:#e5e7eb;font-family:system-ui,sans-serif}}
.glass{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);backdrop-filter:blur(12px)}}
</style></head><body class="min-h-screen">
<div class="max-w-6xl mx-auto px-4 py-8">
<div class="text-center mb-12">
<h1 class="text-4xl font-bold bg-gradient-to-r from-red-500 to-blue-500 bg-clip-text text-transparent">
Spider-Man: Brand New Day</h1>
<p class="text-gray-500 mt-2">Full Scene Storyboard — {len(scene_analysis)} scenes</p>
</div>
<div id="scenes">{scene_cards}</div>
</div></body></html>'''

with open(STORYBOARD, "w") as f:
    f.write(html)

with open(META, "w") as f:
    json.dump({"scenes": scene_analysis, "total": len(scene_analysis)}, f, indent=2)

t_total = time.time()
print(f"\n[Swarm Complete] in {t_total-t1:.1f}s")
print(f"  Scenes: {len(scene_analysis)}")
print(f"  Clips: {len(os.listdir(CLIPS_DIR))}")
print(f"  Storyboard: {STORYBOARD}")
print(f"  Meta: {META}")
