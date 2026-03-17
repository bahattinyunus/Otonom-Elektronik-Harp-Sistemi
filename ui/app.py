from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
from core.orchestrator import SystemOrchestrator
from core.config import UI_HOST, UI_PORT, UPDATE_INTERVAL_MS

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
orchestrator = SystemOrchestrator()

@app.route('/')
def index():
    return render_template('index.html')

def background_thread():
    """Continuously runs the EW cycle and broadcasts to UI."""
    print("Dashboard data stream started...")
    while True:
        results = orchestrator.run_cycle()
        socketio.emit('new_spectrum_data', results)
        time.sleep(UPDATE_INTERVAL_MS / 1000.0)

if __name__ == '__main__':
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    
    print(f"Starting Otonom-EH Dashboard at http://localhost:{UI_PORT}")
    socketio.run(app, host=UI_HOST, port=UI_PORT, debug=False)
