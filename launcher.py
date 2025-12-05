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
subprocess.Popen(
    [
        "bash", "-c",
        f"cd {SCRIPT_DIR} && source venv/bin/activate && python standalone_app.py > /dev/null 2>&1"
    ],
    start_new_session=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Give it a moment to start
import time
time.sleep(0.3)

# Find and close the terminal emulator
try:
    current = psutil.Process(os.getpid())
    
    # Common terminal emulators
    terminals = ['kitty', 'alacritty', 'wezterm', 'foot', 'gnome-terminal', 
                 'konsole', 'xterm', 'terminator', 'tilix', 'st', 'urxvt',
                 'rxvt', 'xfce4-terminal', 'mate-terminal', 'lxterminal']
    
    # Walk up the process tree
    while current:
        name = current.name().lower()
        
        # Check if this is a terminal emulator
        for term in terminals:
            if term in name:
                # Found the terminal, close it
                current.terminate()
                sys.exit(0)
        
        # Move to parent
        try:
            current = current.parent()
        except:
            break
            
except Exception:
    # If we can't close the terminal, just exit silently
    pass

sys.exit(0)
