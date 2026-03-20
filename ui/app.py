import csv
import io
import json
import sqlite3
from flask import Flask, render_template, Response, jsonify
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
    si  = io.StringIO()
    cw  = csv.writer(si)
    cw.writerow(['ID', 'Timestamp', 'Freq_Idx', 'Freq_MHz', 'SNR', 'Type',
                 'Confidence', 'Threat', 'AoA', 'Track_ID', 'RFI_Hash'])
    try:
        with sqlite3.connect("logs/mission_log.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, freq_idx, snr, type, aoa, track_id, rfi_hash "
                "FROM signals ORDER BY timestamp DESC"
            )
            rows = cursor.fetchall()
            cw.writerows(rows)
    except Exception as e:
        cw.writerow(["Error", str(e)])
    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=aar_mission_report.csv"},
    )


@app.route('/api/stats')
def get_stats():
    r = orchestrator.latest_results
    if not r:
        return jsonify({})
    ea = r.get('ea_status', {})
    ss = r.get('spectrum_stats', {})
    return jsonify({
        "target_count":    ea.get('target_count', 0),
        "total_reward":    ea.get('reward', 0),
        "epsilon":         ea.get('epsilon', 1.0),
        "episode":         ea.get('episode', 0),
        "q_states":        ea.get('q_states', 0),
        "occupancy_pct":   ss.get('occupancy_pct', 0),
        "peak_pwr_dbm":    ss.get('peak_pwr_dbm', -100),
        "active_sigs":     ss.get('active_sigs', 0),
        "current_action":  ea.get('action', 'STANDBY'),
    })


@socketio.on('set_mode')
def handle_set_mode(data):
    orchestrator.mode = data.get('mode', 'AUTO')

@socketio.on('set_manual_jam')
def handle_manual_jam(data):
    if orchestrator.mode == 'MANUAL':
        orchestrator.manual_jam = data.get('is_jamming', False)

@socketio.on('set_noise_floor')
def handle_noise_floor(data):
    orchestrator.env.noise_floor = float(data.get('noise', -100))


def background_thread():
    while True:
        results = orchestrator.run_cycle()
        socketio.emit('new_spectrum_data', results)
        time.sleep(UPDATE_INTERVAL_MS / 1000.0)


if __name__ == '__main__':
    t = threading.Thread(target=background_thread, daemon=True)
    t.start()
    print(f"Otonom-EH Dashboard: http://localhost:{UI_PORT}")
    socketio.run(app, host=UI_HOST, port=UI_PORT, debug=False)
