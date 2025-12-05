#!/usr/bin/env python3
"""
Muser Launcher - Minimalist Music Player
Launches the app and attempts to close the terminal window
"""
import os
import sys
import subprocess
import psutil

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Launch the music player in background
# Launch the music player in background
log_file = os.path.join(SCRIPT_DIR, "muser.log")
with open(log_file, "a") as f:
    subprocess.Popen(
        [os.path.join(SCRIPT_DIR, 'venv', 'bin', 'python3'), "-u", "standalone_app.py"],
        cwd=SCRIPT_DIR,
        start_new_session=True,
        stdout=f,
        stderr=subprocess.STDOUT
    )

print(f"Muser launched. Logs: {log_file}")
# Terminal closing logic disabled for debugging
# import time
# time.sleep(0.3)
# ... (rest of the closing logic removed)

sys.exit(0)
