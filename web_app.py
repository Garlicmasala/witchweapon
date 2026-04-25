#!/usr/bin/env python3
"""
Web deployment for Witch's Weapon using Flask.
Serves the game through a web interface using the web platform implementation.
Includes production-ready endpoints and error handling.
"""

from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import sys
import os
import io
import contextlib
import threading
import queue
import time
import builtins
import json
from datetime import datetime
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'witch_weapon_web_secret_key')

# Global game state
game_state = {
    'initialized': False,
    'portability': None,
    'output_buffer': [],
    'input_queue': queue.Queue(),
    'output_queue': queue.Queue(),
    'game_thread': None,
    'running': False,
    'created_at': datetime.now(),
    'session_count': 0,
    'errors': []
}

# HTML templates
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Witch's Weapon - Web Edition</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            text-align: center;
            color: #ff69b4;
            text-shadow: 0 0 10px #ff1493;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .terminal {
            background: #000;
            border: 2px solid #00ff00;
            padding: 20px;
            border-radius: 5px;
            white-space: pre-wrap;
            font-size: 14px;
            min-height: 400px;
            max-height: 600px;
            overflow-y: auto;
        }
        .input-form {
            margin-top: 20px;
        }
        input[type="text"] {
            background: #000;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            width: 300px;
        }
        button {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            cursor: pointer;
            margin-left: 10px;
        }
        button:hover {
            background: #00cc00;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            background: #002200;
            border: 1px solid #00ff00;
        }
        .loading {
            color: #ffff00;
            font-style: italic;
        }
    </style>
    <script>
        function scrollToBottom() {
            var terminal = document.querySelector('.terminal');
            if (terminal) terminal.scrollTop = terminal.scrollHeight;
        }
        window.onload = scrollToBottom;
    </script>
</head>
<body>
    <div class="container">
        <h1>🧙‍♀️ Witch's Weapon - Web Edition</h1>

        <div class="terminal">{{ output|safe }}</div>

        {% if input_needed %}
        <div class="input-form">
            <form method="post">
                <input type="text" name="user_input" placeholder="Enter your choice..." autofocus autocomplete="off">
                <button type="submit">Submit</button>
            </form>
        </div>
        {% endif %}

        <div class="status">
            <strong>Platform:</strong> Web | <strong>UI Mode:</strong> {{ ui_mode }} | <strong>Performance:</strong> {{ perf_tier }}
            <br>
            <a href="/reset" style="color: #ff6600;">[Reset Game]</a> | 
            <a href="/health" style="color: #00ff00;">[Health Check]</a> |
            <a href="/api/status" style="color: #00ff00;">[API Status]</a>
        </div>
    </div>
</body>
</html>
"""

def initialize_game():
    """Initialize the game with web platform."""
    global game_state

    if not game_state['initialized']:
        try:
            from PORTABILITY_GUIDE import initialize_game_for_platform
            game_state['portability'] = initialize_game_for_platform('web')
            game_state['initialized'] = True
            game_state['output_buffer'] = ["🧙‍♀️ Welcome to Witch's Weapon - Web Edition!\n", "Game initialized with web platform.\n"]
        except Exception as e:
            game_state['output_buffer'] = [f"❌ Error initializing game: {e}\n"]
            return False
    return True

def get_game_output():
    """Get the current game output."""
    return ''.join(game_state['output_buffer'])

def get_portability_info():
    """Get portability system information."""
    if game_state['portability']:
        perf_manager = game_state['portability']['perf_manager']
        ui_responsive = game_state['portability']['ui_responsive']
        return {
            'ui_mode': ui_responsive.mode.value.upper(),
            'perf_tier': perf_manager.get_tier().value.upper()
        }
    return {'ui_mode': 'UNKNOWN', 'perf_tier': 'UNKNOWN'}

def web_input(prompt=""):
    """Web-compatible input function."""
    game_state['output_buffer'].append(prompt)
    try:
        user_input = game_state['input_queue'].get(timeout=300)
        game_state['output_buffer'].append(f"> {user_input}\n")
        return user_input
    except queue.Empty:
        return "quit"

def web_print(*args, **kwargs):
    """Web-compatible print function."""
    text = ' '.join(str(arg) for arg in args)
    if kwargs.get('end', '\n') == '\n':
        text += '\n'
    game_state['output_buffer'].append(text)

def run_game():
    """Run the game in a separate thread."""
    global game_state
    old_stdout = sys.stdout
    old_stdin = sys.stdin
    old_input = builtins.input

    try:
        sys.stdout = type('WebStdout', (), {'write': web_print, 'flush': lambda: None})()
        builtins.input = web_input
        import main
        main.main()
    except Exception as e:
        error_msg = f"❌ Game error: {str(e)}\n{traceback.format_exc()}\n"
        web_print(error_msg)
        game_state['errors'].append(str(e))
    finally:
        sys.stdout = old_stdout
        sys.stdin = old_stdin
        builtins.input = old_input
        game_state['running'] = False

def start_game_thread():
    """Start the game in a background thread."""
    global game_state
    if not game_state['running']:
        game_state['running'] = True
        game_state['game_thread'] = threading.Thread(target=run_game, daemon=True)
        game_state['game_thread'].start()

@app.route('/', methods=['GET', 'POST'])
def index():
    global game_state
    if not game_state['initialized']:
        if not initialize_game():
            return "Failed to initialize game"

    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        if user_input:
            game_state['input_queue'].put(user_input)
            if not game_state['running']:
                start_game_thread()
            time.sleep(0.5)

    output = get_game_output()
    portability_info = get_portability_info()
    input_needed = game_state['running'] and not game_state['input_queue'].empty()

    return render_template_string(MAIN_TEMPLATE,
                                output=output,
                                input_needed=input_needed,
                                ui_mode=portability_info['ui_mode'],
                                perf_tier=portability_info['perf_tier'])

@app.route('/reset')
def reset():
    """Reset the game state."""
    global game_state
    game_state['running'] = False
    if game_state['game_thread'] and game_state['game_thread'].is_alive():
        game_state['game_thread'].join(timeout=1)

    game_state = {
        'initialized': False,
        'portability': None,
        'output_buffer': [],
        'input_queue': queue.Queue(),
        'output_queue': queue.Queue(),
        'game_thread': None,
        'running': False,
        'created_at': datetime.now(),
        'session_count': game_state.get('session_count', 0) + 1,
        'errors': []
    }
    return redirect(url_for('index'))

@app.route('/health')
def health():
    """Health check endpoint for deployment."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'initialized': game_state['initialized'],
        'running': game_state['running']
    }), 200

@app.route('/api/status')
def api_status():
    """Get game status as JSON."""
    portability_info = get_portability_info()
    return jsonify({
        'status': 'running' if game_state['running'] else 'idle',
        'initialized': game_state['initialized'],
        'session_count': game_state['session_count'],
        'uptime_seconds': (datetime.now() - game_state['created_at']).total_seconds(),
        'portability': portability_info,
        'buffer_size': len(game_state['output_buffer']),
        'errors': game_state['errors'][-10:]
    }), 200

@app.route('/api/output')
def api_output():
    """Get game output as JSON."""
    output = get_game_output()
    return jsonify({
        'output': output,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/input', methods=['POST'])
def api_input():
    """Submit input via JSON API."""
    global game_state
    try:
        data = request.get_json()
        user_input = data.get('input', '').strip()
        
        if user_input:
            game_state['input_queue'].put(user_input)
            if not game_state['running']:
                start_game_thread()
            time.sleep(0.5)
        
        return jsonify({
            'success': True,
            'input': user_input,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        error_msg = str(e)
        game_state['errors'].append(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'status': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    error_msg = str(error)
    game_state['errors'].append(error_msg)
    return jsonify({
        'error': 'Internal Server Error',
        'message': error_msg,
        'status': 500
    }), 500

@app.before_request
def log_request():
    """Log incoming requests."""
    if app.debug:
        print(f"[{datetime.now().isoformat()}] {request.method} {request.path}")

@app.after_request
def add_headers(response):
    """Add security headers to responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    is_production = os.environ.get('FLASK_ENV') == 'production'
    port = int(os.environ.get('PORT', 5000))
    app.debug = not is_production
    
    print("")
    print("🧙‍♀️ Witch's Weapon - Web Edition")
    print("=" * 50)
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📊 Status: http://localhost:{port}/health")
    print(f"🎮 Game API: http://localhost:{port}/api/status")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    print("")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.debug,
        threaded=True,
        use_reloader=False
    )
