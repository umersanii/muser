#!/usr/bin/env python3
"""
Standalone Music Player App
Launches the web player in a native window using PyWebView
"""
import webview
import threading
import time
import os
import sys
from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
from player_backend import PlayerBackend
from urllib.parse import unquote

# Flask app setup
app = Flask(__name__)
CORS(app)

# Initialize player
try:
    player = PlayerBackend()
except RuntimeError as e:
    print(f"Error initializing player: {e}")
    player = None

@app.route('/')
def index():
    return send_file('web_player.html')

@app.route('/local-file/<path:filepath>')
def serve_local_file(filepath):
    """Serve local files (for album art)"""
    filepath = unquote(filepath)
    if filepath.startswith('file://'):
        filepath = filepath[7:]
    
    # Decode URL-encoded spaces
    filepath = filepath.replace('%20', ' ')
    
    if os.path.exists(filepath):
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        return send_from_directory(directory, filename)
    return '', 404

@app.route('/api/status')
def get_status():
    if not player:
        return jsonify({
            'status': 'Stopped',
            'metadata': {'title': 'No Media', 'artist': 'Unknown Artist'},
            'position': 0,
            'length': 0
        })
    
    status = player.get_status()
    metadata = player.get_metadata()
    position = player.get_position()
    length = metadata.get('length', 0)
    
    # Convert file:// URLs to local server URLs
    art_url = metadata.get('art_url', '')
    if art_url.startswith('file://'):
        art_url = f'/local-file/{art_url}'
    
    return jsonify({
        'status': status,
        'metadata': {
            'title': metadata.get('title', 'Unknown'),
            'artist': metadata.get('artist', 'Unknown Artist'),
            'art_url': art_url
        },
        'position': position,
        'length': length
    })

@app.route('/api/play_pause', methods=['POST'])
def play_pause():
    if player:
        player.play_pause()
    return jsonify({'success': True})

@app.route('/api/next', methods=['POST'])
def next_track():
    if player:
        player.next()
    return jsonify({'success': True})

@app.route('/api/prev', methods=['POST'])
def prev_track():
    if player:
        player.previous()
    return jsonify({'success': True})

@app.route('/api/seek/<float:percentage>', methods=['POST'])
def seek(percentage):
    if player:
        metadata = player.get_metadata()
        length = metadata.get('length', 0)
        if length > 0:
            target_time = percentage * length
            player.set_position(target_time)
    return jsonify({'success': True})

def start_flask(port):
    """Start Flask server in background"""
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except OSError:
        pass

def find_free_port():
    """Find a free port to use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

if __name__ == '__main__':
    # Find a free port
    port = find_free_port()
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask, args=(port,), daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start
    time.sleep(1)
    
    # Create PyWebView window
    try:
        window = webview.create_window(
            '🎵 Music Player',
            f'http://127.0.0.1:{port}',
            width=500,
            height=750,
            resizable=True,
            background_color='#1e1e2e',
            frameless=False,
            easy_drag=True,
            min_size=(300, 200)
        )
        
        # Start the GUI (blocks until window closes)
        webview.start(debug=False)
    except Exception as e:
        print(f"Error starting window: {e}")
        print("Make sure you have PyQt6 or GTK installed:")
        print("  pip install PyQt6 PyQt6-WebEngine")
        sys.exit(1)

