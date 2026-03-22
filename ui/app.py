import csv
import io
import sqlite3
from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO
import threading
import time
from core.orchestrator import SystemOrchestrator
from core.config import UI_HOST, UI_PORT, UPDATE_INTERVAL_MS

import subprocess
import os
import signal

app          = Flask(__name__)
socketio     = SocketIO(app, cors_allowed_origins="*")
orchestrator = SystemOrchestrator()

# --- Simulation Management ---
sim_proc = None

def start_external_simulator():
    global sim_proc
    if sim_proc and sim_proc.poll() is None:
        return # Already running
    
    env_path = os.getcwd()
    # Use the same python executable and set PYTHONPATH
    my_env = os.environ.copy()
    my_env["PYTHONPATH"] = env_path + os.pathsep + my_env.get("PYTHONPATH", "")
    
    script_path = os.path.join(env_path, "sim", "external_signals_source.py")
    try:
        sim_proc = subprocess.Popen(
            [sys.executable, script_path],
            env=my_env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
    except Exception as e:
        print(f"[!] Simülatör başlatma hatası: {e}")

def stop_external_simulator():
    global sim_proc
    if sim_proc:
        if os.name == 'nt':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(sim_proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            sim_proc.terminate()
        sim_proc = None

import sys


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/export_report')
def export_report():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Timestamp', 'Freq_Idx', 'Freq_MHz', 'SNR', 'Type',
                 'Confidence', 'Threat', 'AoA', 'DF_Confidence',
                 'Track_ID', 'Track_Hits', 'RFI_Hash'])
    try:
        with sqlite3.connect("logs/mission_log.db") as conn:
            c = conn.cursor()
            c.execute(
                "SELECT id, timestamp, freq_idx, freq_mhz, snr, type, confidence, "
                "threat_level, aoa, df_confidence, track_id, track_hits, rfi_hash "
                "FROM signals ORDER BY timestamp DESC"
            )
            cw.writerows(c.fetchall())
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
        "target_count":   ea.get('target_count', 0),
        "total_reward":   ea.get('reward', 0),
        "epsilon":        ea.get('epsilon', 1.0),
        "episode":        ea.get('episode', 0),
        "q_states":       ea.get('q_states', 0),
        "occupancy_pct":  ss.get('occupancy_pct', 0),
        "peak_pwr_dbm":   ss.get('peak_pwr_dbm', -100),
        "active_sigs":    ss.get('active_sigs', 0),
        "current_action": ea.get('action', 'STANDBY'),
        "rf_source":      ss.get('rf_source', 'LOCAL'),
        "denoiser_on":    ss.get('denoiser_on', True),
    })


@app.route('/api/history')
def get_history():
    return jsonify(orchestrator.logger.get_recent_signals(50))


@app.route('/api/threats')
def get_threats():
    return jsonify({
        "threat_stats": orchestrator.logger.get_threat_stats(300),
        "type_stats":   orchestrator.logger.get_type_stats(300),
        "actions":      orchestrator.logger.get_action_history(20),
    })


# ── HIL Telemetry API v1 (New V7) ──────────────────────────────────────────
@app.route('/api/v1/telemetry')
def get_v1_telemetry():
    """HIL-Ready REST endpoint for external mission controllers."""
    r = orchestrator.latest_results
    if not r:
        return jsonify({"status": "unavailable"}), 503
    
    return jsonify({
        "version": "6.0.0", # System core version
        "timestamp": r.get("timestamp"),
        "swarm": orchestrator.friendly_nodes,
        "intel": {
            "signals": [
                {k: v for k, v in s.items() if k not in ["waterfall_slice"]} 
                for s in r.get("signals", [])
            ],
            "stats": r.get("spectrum_stats")
        },
        "action": r.get("ea_status")
    })


# ── Socket events ─────────────────────────────────────────────────────────────
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


@socketio.on('set_denoiser')
def handle_denoiser(data):
    orchestrator.denoiser_on = bool(data.get('enabled', True))


@socketio.on('control_sim')
def handle_sim_control(data):
    cmd = data.get('command')
    if cmd == 'START':
        start_external_simulator()
    elif cmd == 'STOP':
        stop_external_simulator()
    elif cmd == 'RESTART':
        stop_external_simulator()
        time.sleep(0.5)
        start_external_simulator()


# ── Background emitter ────────────────────────────────────────────────────────
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
