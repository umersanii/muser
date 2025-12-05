import subprocess
import shutil
import json

class PlayerBackend:
    def __init__(self):
        self.playerctl = shutil.which("playerctl")
        if not self.playerctl:
            raise RuntimeError("playerctl not found. Please install it.")

    def _run_command(self, args):
        try:
            result = subprocess.run(
                [self.playerctl] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_metadata(self):
        # format: {{ title }}|{{ artist }}|{{ album }}|{{ mpris:artUrl }}|{{ mpris:length }}
        fmt = "{{ title }}|{{ artist }}|{{ album }}|{{ mpris:artUrl }}|{{ mpris:length }}"
        output = self._run_command(["metadata", "--format", fmt])
        if not output:
            return {
                "title": "No Media",
                "artist": "Unknown",
                "album": "Unknown",
                "art_url": "",
                "length": 0
            }
        
        parts = output.split("|")
        # Handle potential missing fields if split doesn't return enough parts
        # This is a basic implementation; robust parsing might be needed
        if len(parts) < 5:
             return {
                "title": "Unknown",
                "artist": "Unknown",
                "album": "Unknown",
                "art_url": "",
                "length": 0
            }

        length_micro = parts[4]
        length_sec = 0
        if length_micro:
            try:
                length_sec = int(length_micro) / 1000000
            except ValueError:
                pass

        return {
            "title": parts[0],
            "artist": parts[1],
            "album": parts[2],
            "art_url": parts[3],
            "length": length_sec
        }

    def get_position(self):
        output = self._run_command(["position"])
        if output:
            try:
                return float(output)
            except ValueError:
                return 0.0
        return 0.0

    def get_status(self):
        return self._run_command(["status"])

    def play_pause(self):
        self._run_command(["play-pause"])

    def next(self):
        self._run_command(["next"])

    def previous(self):
        self._run_command(["previous"])

    def seek(self, offset):
        # offset in seconds, can be negative
        # playerctl position [offset][+/-]
        sign = "+" if offset >= 0 else "-"
        self._run_command(["position", f"{abs(offset)}{sign}"])

    def set_position(self, position):
        self._run_command(["position", str(position)])
    
    def shuffle(self):
        self._run_command(["shuffle", "toggle"])
        
    def loop(self):
        # playerctl loop [None|Track|Playlist]
        # This is a toggle implementation, cycling through
        current = self._run_command(["loop"])
        if current == "None":
            self._run_command(["loop", "Playlist"])
        elif current == "Playlist":
            self._run_command(["loop", "Track"])
        else:
            self._run_command(["loop", "None"])

    def get_shuffle_status(self):
        return self._run_command(["shuffle"])

    def get_loop_status(self):
        return self._run_command(["loop"])
