#!/usr/bin/env python3
import subprocess, os, json, re, shutil
from pathlib import Path

BASE = os.path.expanduser("~/projects/yonjan-video-ai/spiderman-frames")
VIDEO = os.path.join(BASE, "spiderman-bnd-720p.mp4")
FRAMES_DIR = os.path.join(BASE, "frames")
CLIPS_DIR = os.path.join(BASE, "scene_clips")
PREVIEW = os.path.join(BASE, "scene_preview.html")
META = os.path.join(BASE, "scene_meta.json")

os.makedirs(CLIPS_DIR, exist_ok=True)

# Step 1: Detect scene timestamps
print("[1/4] Detecting scenes...")
result = subprocess.run(
    ["ffmpeg", "-i", VIDEO, "-vf", "select=gt(scene\\,0.3),showinfo", "-vsync", "0", "-f", "null", "-"],
    capture_output=True, timeout=30
)
stderr = result.stderr.decode()
timestamps = []
for line in stderr.split('\n'):
    m = re.search(r'pts_time:([0-9.]+)', line)
    if m:
        timestamps.append(float(m.group(1)))
print(f"  Found {len(timestamps)} scene changes")

# Step 2: Build scene ranges (start -> end)
scenes = []
prev = 0.0
for t in timestamps:
    scenes.append({"num": len(scenes)+1, "start": prev, "end": t})
    prev = t
scenes.append({"num": len(scenes)+1, "start": prev, "end": 162.0})
print(f"  Built {len(scenes)} scene ranges")

# Step 3: Map frame files to scenes and extract first 2
print("[2/4] Mapping frames to scenes...")
frame_names = sorted(os.listdir(FRAMES_DIR), key=lambda x: int(re.sub(r'\D', '', x)))
scene_map = {}

for fname in frame_names:
    sec = int(re.sub(r'\D', '', fname))
    for s in scenes:
        if s["start"] <= sec < s["end"]:
            scene_map.setdefault(s["num"], []).append(fname)
            break

print(f"  Frames per scene: {[(k, len(v)) for k,v in sorted(scene_map.items())[:5]]}")

# Step 4: Extract first 2 scene video clips
print("[3/4] Extracting first 2 scene clips...")
clip_paths = []
for s in scenes[:2]:
    start = s["start"]
    end = s["end"]
    num = s["num"]
    out = os.path.join(CLIPS_DIR, f"scene_{num:03d}.mp4")
    dur = end - start
    print(f"  Scene {num}: {start:.1f}s -> {end:.1f}s ({dur:.1f}s) -> {out}")
    subprocess.run(
        ["ffmpeg", "-ss", str(start), "-i", VIDEO, "-to", str(dur),
         "-c", "copy", "-avoid_negative_ts", "make_zero", "-y", out],
        capture_output=True, timeout=30
    )
    clip_paths.append(out)

# Step 5: Generate preview HTML
print("[4/4] Generating preview HTML...")
scene_cards = ""
for i, s in enumerate(scenes[:2]):
    frames_html = ""
    for fname in scene_map.get(s["num"], []):
        frames_html += f'<img src="frames/{fname}" class="w-20 h-12 object-cover rounded cursor-pointer hover:ring-2 hover:ring-indigo-400" onclick="document.getElementById(\'player-{i}\').src=\'scene_clips/scene_{s["num"]:03d}.mp4\'">'
    scene_cards += f'''
    <div class="mb-8">
        <h2 class="text-lg font-semibold text-white mb-2">Scene {s["num"]}: {s["start"]:.1f}s - {s["end"]:.1f}s</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="glass rounded-2xl p-3">
                <video id="player-{i}" class="w-full rounded-xl" controls>
                    <source src="scene_clips/scene_{s["num"]:03d}.mp4" type="video/mp4">
                </video>
            </div>
            <div class="glass rounded-2xl p-4">
                <div class="text-xs text-indigo-400 mb-2">Frames ({len(scene_map.get(s["num"], []))})</div>
                <div class="flex flex-wrap gap-1">{frames_html}</div>
            </div>
        </div>
    </div>'''

html = f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Scene Preview</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:#0a0a0f;color:#e5e7eb;font-family:system-ui,sans-serif}}
.glass{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);backdrop-filter:blur(12px)}}
</style></head><body class="min-h-screen p-8">
<div class="max-w-5xl mx-auto">
<h1 class="text-3xl font-bold mb-2 bg-gradient-to-r from-red-500 to-blue-500 bg-clip-text text-transparent">Spider-Man: Scene Preview</h1>
<p class="text-gray-500 mb-8">First 2 scenes extracted from trailer</p>
{scene_cards}
</div></body></html>'''

with open(PREVIEW, "w") as f:
    f.write(html)

# Save metadata
with open(META, "w") as f:
    json.dump({"scenes": scenes[:2], "total_scenes": len(scenes), "clip_dir": CLIPS_DIR, "preview": PREVIEW}, f, indent=2)

print(f"\nDone! Preview: {PREVIEW}")
print(f"Clips: {CLIPS_DIR}")
