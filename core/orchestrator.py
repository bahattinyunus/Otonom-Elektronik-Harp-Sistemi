import time
import numpy as np
import random
from sim.rf_environment import RFEnvironment
from modules.detector.detector import WaterfallDetector
from modules.classifier.classifier import ModulationClassifier
from modules.direction_finder.df_logic import DirectionFinder
from modules.optimizer.et_optimizer import SmartOptimizer
from modules.tracker.advanced_tracker import AdvancedTracker
from modules.denoiser.neural_denoiser import NeuralDenoiser
from modules.synthesizer.waveform_gen import WaveformSynthesizer
from modules.predictor.hop_predictor import FrequencyHopPredictor
from modules.optimizer.ep_agent import EPAgent
from modules.analytics.mission_analyzer import MissionAnalyzer
from core.mission_control import MissionStateMachine, MissionState
from core.config import NOISE_FLOOR, SDR_TYPE
from core.blackbox import MissionLogger
from sim.rf_environment import RFEnvironment


from core.real_sdr import RealSDR

class SystemOrchestrator:
    """Main brain of the system. Routes data between all processing modules."""

    def __init__(self):
        # SDR Hardware Abstraction Layer (HAL)
        if SDR_TYPE == "SIMULATED":
            self.env = RFEnvironment()
        else:
            self.env = RealSDR() 
        self.detector   = WaterfallDetector()
        self.classifier = ModulationClassifier()
        self.df         = DirectionFinder()
        self.optimizer  = SmartOptimizer()
        self.tracker    = AdvancedTracker()
        self.denoiser   = NeuralDenoiser()
        self.synth      = WaveformSynthesizer()
        self.predictor  = FrequencyHopPredictor()
        self.ep_agent   = EPAgent()
        self.analyzer   = MissionAnalyzer()
        self.logger     = MissionLogger("logs/mission_log.db")
        
        self.mission_control = MissionStateMachine()
        self.jamming_cycle_idx = 0  # Multi-target slicing (V1.0)
        self.module_health = {
            "HAL": True, "DET": True, "CLS": True, "DF": True, 
            "OPT": True, "TRK": True, "DNS": True, "SYN": True
        }

        self.mode           = "AUTO"
        self.manual_jam     = False
        self.denoiser_on    = True
        self.latest_results = {}

        # Swarm Collaborative Intelligence (V7)
        self.friendly_nodes = [
            {"id": "NODE-01", "role": "SCOUT", "freq_mhz": 433.100, "rfi_hash": "0xA1B2C"},
            {"id": "NODE-02", "role": "COMMS", "freq_mhz": 433.850, "rfi_hash": "0xF9E8D"}
        ]

    def _idx_to_mhz(self, freq_idx: int) -> float:
        freq_hz = (freq_idx / self.env.fft_size) * self.env.fs + (self.env.center_freq - self.env.fs / 2)
        return round(freq_hz / 1e6, 3)

    def run_cycle(self):
        # 1. Spectrum Acquisition (HAL)
        try:
            psd_raw = self.env.generate_spectrum_frame()
            self.module_health["HAL"] = self.env.is_active()
        except Exception as e:
            print(f"[Orch] HAL Error: {e}")
            self.module_health["HAL"] = False
            psd_raw = [-100.0] * 1024 # Emergency fallback

        hz_per_bin = self.env.fs / self.env.fft_size

        # 2. Cognitive Denoising
        try:
            psd_proc = self.denoiser.process(psd_raw) if self.denoiser_on else psd_raw
            self.module_health["DNS"] = True
        except Exception as e:
            print(f"[Orch] Denoising Error: {e}")
            self.module_health["DNS"] = False
            psd_proc = psd_raw

        # 3. Detection & Feature Extraction
        try:
        # 4. Predict next hop for tracking targets
        for sig in processed_signals:
            track_id = sig.get("track_id")
        # 4. Advanced Tracking & Mission Update
        try:
            processed_signals = self.tracker.update(processed_signals)
            for sig in processed_signals:
                track_id = sig.get("track_id")
                if track_id:
                    prediction = self.predictor.update_and_predict(track_id, sig["freq_mhz"])
                    if prediction:
                        sig["predicted_next_mhz"] = round(float(prediction), 3)

            mission_state = self.mission_control.update(processed_signals)
            self.module_health["TRK"] = True
        except Exception as e:
            print(f"[Orch] Tracking Error: {e}")
            self.module_health["TRK"] = False
            mission_state = MissionState.SCAN

        # 4.5. Autonomous Frequency Chasing
        if mission_state in [MissionState.TRACK, MissionState.ENGAGE, MissionState.EVALUATE]:
            target_ids = self.mission_control.target_track_ids
            if target_ids:
                primary_id = target_ids[0]
                target_sig = next((s for s in processed_signals if s.get("track_id") == primary_id), None)
                if target_sig:
                    rel_pos = target_sig["freq_idx"] / self.env.fft_size
                    if rel_pos < 0.15 or rel_pos > 0.85:
                        self.env.set_center_freq(target_sig["freq_mhz"] * 1e6)

        # 5. Electronic Attack (EA) Strategy
        try:
            if self.mode == "AUTO":
                if mission_state == MissionState.ENGAGE:
                    targets = self.mission_control.target_track_ids
                    if targets:
                        active_target_id = targets[self.jamming_cycle_idx % len(targets)]
                        self.jamming_cycle_idx += 1
                        target_sig = next((s for s in processed_signals if s.get("track_id") == active_target_id), None)
                        
                        if target_sig:
                            # Pass friendly registry to avoid fratricide reward penalty (V1.2)
                            ea_status = self.optimizer.update_strategy([target_sig], self.friendly_nodes)
                            self.env.set_jamming(ea_status.get("action", "JAM_SPOT"))
                            ea_status["status"] = f"TAARRUZ: ID#{active_target_id}"
                        else:
                            ea_status = {"action": "STANDBY", "is_jamming": False, "status": "HEDEF KAYIP"}
                    else:
                        ea_status = {"action": "STANDBY", "is_jamming": False, "status": "HEDEF YOK"}
                elif mission_state == MissionState.EVALUATE:
                    ea_status = {"is_jamming": False, "status": "BDA (ANALİZ)", "action": "STANDBY"}
                    self.env.set_jamming("STANDBY")
                else:
                    ea_status = {"is_jamming": False, "status": f"TAKTİKİ: {mission_state.value}", "action": "STANDBY"}
                    self.env.set_jamming("STANDBY")
            else:
                is_jam = self.manual_jam
                ea_status = {"is_jamming": is_jam, "action": "JAM_SPOT" if is_jam else "STANDBY"}
                self.env.set_jamming(ea_status["action"])
            self.module_health["OPT"] = True
        except Exception as e:
            print(f"[Orch] Strategy error: {e}")
            self.module_health["OPT"] = False
            ea_status = {"action": "STANDBY", "is_jamming": False, "status": "ARIZA (OPT)"}

        # 5. Cognitive Synthesis Logic (V8)
        try:
            if len(processed_signals) > 0 and self.mode == "AUTO":
                # Create a phantom target as a decoy if 1+ real threats are detected
                if not self.synth.active_phantoms:
                    self.synth.create_phantom_target("DECOY", 1200000, 30.0)
            else:
                self.synth.clear_phantoms()
            self.module_health["SYN"] = True
        except Exception as e:
            print(f"[Orch] Synthesis Error: {e}")
            self.module_health["SYN"] = False

        self.logger.log_signals(processed_signals)
        self.logger.log_action(ea_status)

        # Per-cycle threat counts for the UI summary bar
        threat_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for s in processed_signals:
            lvl = s.get("threat_level", "LOW")
            threat_counts[lvl] = threat_counts.get(lvl, 0) + 1

        # 6. Final Results & Telemetry
        try:
            ep_status = self.ep_agent.decide_action(processed_signals)
            self.analyzer.update({"signals": processed_signals, "ea_status": ea_status, "ep_status": ep_status})
            
            psd_arr = np.array(psd_raw)
            synth_overlay = self.synth.get_spectrum_overlay(len(psd_raw))
            psd_viz = (psd_arr + np.array(synth_overlay)).tolist()
            
            # Simulate small swarm status updates for UI "liveness"
            for node in self.friendly_nodes:
                if random.random() > 0.95:
                    node["status"] = random.choice(["CONNECTED", "SYNCING", "RELAYING"])
                else:
                    node["status"] = node.get("status", "CONNECTED")

            self.latest_results = {
                "waterfall":      psd_viz, 
                "signals":        processed_signals,
                "ea_status":      ea_status,
                "ep_status":      ep_status,
                "mission_report": self.analyzer.generate_strategic_summary(),
                "mission_metrics": self.analyzer.get_mission_metrics(),
                "spectrum_stats": {
                    "peak_pwr_dbm": round(float(np.max(psd_arr)), 1),
                    "active_sigs":  len(self.env.active_signals),
                    "denoiser_on":  self.denoiser_on,
                },
                "health":         self.module_health,
                "sys_mode":       self.mode,
                "timestamp":      time.time(),
                "threat_counts":  threat_counts,
                "swarm":          self.friendly_nodes,
            }
        except Exception as e:
            print(f"[Orch] Final Synthesis Error: {e}")

        return self.latest_results


if __name__ == "__main__":
    orch    = SystemOrchestrator()
    results = orch.run_cycle()
    print(f"Orchestrator cycle OK. Signals: {len(results['signals'])}")
