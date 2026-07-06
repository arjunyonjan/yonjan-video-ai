# Ollama on Termux — Honor90 Android

## Setup (2026-07-06)

```bash
# Fix dpkg first
dpkg --configure -a

# Update system
apt update && apt upgrade -y

# Change repos (selected Asia mirrors)
termux-change-repo

# Install Ollama
pkg install ollama -y

# Start server
ollama serve &

# Pull model — used all Asia servers when prompted
ollama pull moondream
```

## Performance

- **Device:** Honor90 Android
- **Download speed:** 35+ MB/s (used Asia mirror servers)
- **Auto-selected:** All Asia servers when prompted during setup

## Notes

- OLLAMA_HOST env may need setting for external access
- `ollama serve &` runs in background via Termux
- Moondream is a lightweight vision-language model suitable for mobile
