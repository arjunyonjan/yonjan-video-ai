#!/usr/bin/env python3
import json, re, subprocess, time, os, glob

BASE = os.path.expanduser("~/projects/ai-vision/spiderman-frames")
os.chdir(BASE)

with open("results.json") as f:
    results = json.load(f)

all_frames = sorted(glob.glob("frame_*.jpg"))
todo = [f for f in all_frames if f not in results]

print(f"Total: {len(all_frames)} frames, Done: {len(results)}, TODO: {len(todo)}")
print()

for fname in todo:
    num = fname.replace("frame_", "").replace(".jpg", "")
    print(f"[{num}/{len(all_frames)}] {fname}...", flush=True)
    
    start = time.time()
    try:
        r = subprocess.run(
            ["ollama", "run", "moondream", f"describe {os.path.join(BASE, fname)}"],
            capture_output=True, text=True, timeout=180
        )
        elapsed = time.time() - start
        ms = int(elapsed * 1000)
        
        raw = r.stdout or ""
        raw = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw)
        raw = re.sub(r'\x1b\][0-9;]*[a-zA-Z]', '', raw)
        raw = re.sub(r'\x1b\[?2026[hl]', '', raw)
        raw = re.sub(r'\x1b\[?25[hl]', '', raw)
        raw = re.sub(r'\x1b\[K', '', raw)
        raw = re.sub(r'\[?[0-9]+[DK]', ' ', raw)
        raw = re.sub(r'Added image.*?(?=[A-Za-z])', '', raw, flags=re.DOTALL)
        raw = re.sub(r'\s+', ' ', raw).strip()
        desc = raw
        
        try:
            ocr = subprocess.run(
                ["tesseract", fname, "stdout", "-l", "eng"],
                capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except:
            ocr = ""
        
        results[fname] = {"desc": desc, "ms": ms, "ocr": ocr}
        
        with open("results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"  ✓ {ms}ms: {desc[:60]}...", flush=True)
        
    except subprocess.TimeoutExpired:
        print(f"  ✗ TIMEOUT after 180s", flush=True)
        results[fname] = {"desc": "TIMEOUT", "ms": 0, "ocr": ""}
        with open("results.json", "w") as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        print(f"  ✗ ERROR: {e}", flush=True)
        results[fname] = {"desc": f"ERROR: {e}", "ms": 0, "ocr": ""}
        with open("results.json", "w") as f:
            json.dump(results, f, indent=2)

print(f"\nDone. {len(results)}/{len(all_frames)} frames analyzed.")
