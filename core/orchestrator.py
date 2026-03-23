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
