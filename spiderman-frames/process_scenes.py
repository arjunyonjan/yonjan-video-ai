#!/usr/bin/env python3
"""Process remaining scene frames one by one with setsid persistence"""
import subprocess, json, re, time, os, sys

BASE = os.path.expanduser("~/projects/ai-vision/spiderman-frames")
os.chdir(BASE)

with open("results.json") as f:
    results = json.load(f)

done = set(results.keys())
all_scenes = sorted([f for f in os.listdir(".") if f.startswith("scene_") and f.endswith(".jpg")])
todo = [f for f in all_scenes if f not in done]

if not todo:
    print("All done!")
    sys.exit(0)

for fname in todo:
    num = fname.replace("scene_","").replace(".jpg","")
    fpath = os.path.join(BASE, fname)
    
    print(f"\n[{num}/{len(all_scenes)}] {fname}")
    print(f"Started: {time.strftime('%H:%M:%S')}")
    sys.stdout.flush()
    
    start = time.time()
    try:
        r = subprocess.run(
            ["ollama", "run", "moondream", f"describe {fpath}"],
            capture_output=True, text=True, timeout=300)
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
        
        results[fname] = {"desc": raw, "ms": ms, "ocr": ""}
        print(f"  OK {ms}ms: {raw[:80]}...")
        
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after 300s")
        results[fname] = {"desc": "TIMEOUT", "ms": 0, "ocr": ""}
    except Exception as e:
        print(f"  ERROR: {e}")
        results[fname] = {"desc": f"ERROR: {e}", "ms": 0, "ocr": ""}
    
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved. Elapsed: {time.time()-start:.0f}s")
    sys.stdout.flush()

print(f"\nDone. {len(results)}/{len(all_scenes)} scenes analyzed.")
