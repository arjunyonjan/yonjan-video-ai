#!/data/data/com.termux/files/usr/bin/python3
import subprocess, re, time, json, os, shutil

IMAGES = [
    ("file01.png", "PNG file 01"),
    ("file02.png", "PNG file 02"),
    ("file03.png", "PNG file 03"),
    ("file04.png", "PNG file 04"),
    ("img05.jpg", "Camera photo Jul 3"),
    ("insta-modal.jpg", "Instagram Modal"),
    ("insta-main.jpg", "Instagram Main"),
    ("fb-main.jpg", "Facebook Main"),
    ("insta-old.jpg", "Instagram (older)"),
]

BASE = os.path.expanduser("~/projects/ai-vision")
RESULTS_FILE = os.path.join(BASE, "analysis_results.json")

def analyze(path):
    full = os.path.join(BASE, "images", path)
    start = time.time()
    r = subprocess.run(
        ["ollama", "run", "moondream", f"describe {full}"],
        capture_output=True, text=True, timeout=120
    )
    elapsed = time.time() - start
    out = r.stdout or ""
    # Strip ANSI escape codes
    out = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', out)
    out = re.sub(r'\x1b\][0-9;]*[a-zA-Z]', '', out)
    out = re.sub(r'\x1b\[?2026[hl]', '', out)
    out = re.sub(r'\x1b\[?25[hl]', '', out)
    out = re.sub(r'\x1b\[K', '', out)
    out = re.sub(r'\[4D\[K.*?\[5D\[K', ' ', out)
    out = re.sub(r'\[[0-9]+D\[K', ' ', out)
    out = re.sub(r'\[[0-9]+D', ' ', out)
    out = re.sub(r'\[K', '', out)
    # Remove spinner chars but keep text
    lines = []
    for line in out.split('\n'):
        line = line.strip()
        # skip empty or single-char spinner lines
        if len(line) < 3 and line in '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏⠿⠛⠞⠟⠯⠽⠻⠪⠩⠨⠧⠄.·':
            continue
        if line and not line.startswith('Added image'):
            lines.append(line)
    desc = ' '.join(lines).strip()
    # Clean up repeated spaces
    desc = re.sub(r' +', ' ', desc)
    # If we got nothing useful, try to get the raw output differently
    if len(desc) < 10:
        desc = out[-500:] if len(out) > 500 else out
        desc = re.sub(r'\s+', ' ', desc).strip()
    return desc, elapsed

results = []
for fname, label in IMAGES:
    print(f"Analyzing {label} ({fname})...")
    try:
        desc, elapsed = analyze(fname)
        ms = int(elapsed * 1000)
        results.append({"file": fname, "label": label, "desc": desc, "time_ms": ms})
        print(f"  {ms}ms: {desc[:80]}...")
    except Exception as e:
        results.append({"file": fname, "label": label, "desc": f"ERROR: {e}", "time_ms": 0})
        print(f"  FAILED: {e}")
    # Small delay between runs
    time.sleep(0.5)

with open(RESULTS_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone. Results saved to {RESULTS_FILE}")
total = sum(r["time_ms"] for r in results)
print(f"Total time: {total}ms = {total/1000:.1f}s | Avg: {total/len(results)}ms")
