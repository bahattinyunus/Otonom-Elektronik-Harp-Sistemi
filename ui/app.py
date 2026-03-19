import csv
import io
import sqlite3
from flask import Flask, render_template, Response
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

@app.route('/api/export_report')
def export_report():
    """Generates a CSV report from the mission_log.db signals table."""
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Timestamp', 'Freq_Idx', 'SNR', 'Type', 'AoA', 'Track_ID', 'RFI_Hash'])
    
    try:
        with sqlite3.connect("logs/mission_log.db") as conn:
            cursor = conn.cursor()
            # Fetch all signals
            cursor.execute("SELECT id, timestamp, freq_idx, snr, type, aoa, track_id, rfi_hash FROM signals ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            cw.writerows(rows)
    except Exception as e:
        print(f"Error exporting DB: {e}")
        cw.writerow(["Error", str(e)])

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=aar_mission_report.csv"}
    )


@socketio.on('set_mode')
def handle_set_mode(data):
    mode = data.get('mode', 'AUTO')
    orchestrator.mode = mode
    print(f"System Mode Changed to: {mode}")

@socketio.on('set_manual_jam')
def handle_manual_jam(data):
    if orchestrator.mode == 'MANUAL':
        is_jam = data.get('is_jamming', False)
        orchestrator.manual_jam = is_jam
        print(f"Manual Jamming: {is_jam}")

@socketio.on('set_noise_floor')
def handle_noise_floor(data):
    noise = float(data.get('noise', -100))
    orchestrator.env.noise_floor = noise
    print(f"Noise Floor Changed to: {noise} dB")


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
