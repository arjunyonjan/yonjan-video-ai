#!/usr/bin/env python3
import subprocess, re, time, json, os, sys

DIR = os.path.expanduser("~/projects/ai-vision/images/compressed")
RESULT_FILE = os.path.expanduser("~/projects/ai-vision/results.json")

IMAGES = [
    "file01.jpg", "file02.jpg", "file03.jpg", "file04.jpg",
    "img05.jpg", "insta-modal.jpg", "insta-main.jpg", "fb-main.jpg", "insta-old.jpg"
]

# Load existing results if any
results = {}
if os.path.exists(RESULT_FILE):
    with open(RESULT_FILE) as f:
        results = json.load(f)

for img in IMAGES:
    if img in results:
        print(f"[SKIP] {img} already done")
        continue

    path = os.path.join(DIR, img)
    if not os.path.exists(path):
        print(f"[MISS] {img} not found")
        continue

    print(f"[{IMAGES.index(img)+1}/9] {img}...", flush=True)
    start = time.time()

    try:
        r = subprocess.run(
            ["ollama", "run", "moondream", f"describe {path}"],
            capture_output=True, text=True, timeout=180
        )
        elapsed = time.time() - start
        out = r.stdout or ""
        # Strip ANSI
        out = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', out)
        out = re.sub(r'\x1b\][0-9;]*[a-zA-Z]', '', out)
        out = re.sub(r'\x1b\[?2026[hl]', '', out)
        out = re.sub(r'\x1b\[?25[hl]', '', out)
        out = re.sub(r'\x1b\[K', '', out)
        out = re.sub(r'\[?[0-9]+[DK]', ' ', out)
        out = re.sub(r'\s+', ' ', out).strip()
        # Remove "Added image" line
        out = re.sub(r'^Added image.*?(?=[A-Z])', '', out).strip()

        ms = int(elapsed * 1000)
        results[img] = {"desc": out[:500], "ms": ms}
        print(f"  ✓ {ms}ms: {out[:80]}...")

    except subprocess.TimeoutExpired:
        results[img] = {"desc": "TIMEOUT", "ms": 0}
        print(f"  ✗ TIMEOUT")
    except Exception as e:
        results[img] = {"desc": f"ERROR: {e}", "ms": 0}
        print(f"  ✗ {e}")

    # Save incrementally
    with open(RESULT_FILE, "w") as f:
        json.dump(results, f, indent=2)

print(f"\nDone. {len(results)}/9 images analyzed.")
for img, data in results.items():
    print(f"  {img}: {data['ms']}ms {data['desc'][:60]}...")
