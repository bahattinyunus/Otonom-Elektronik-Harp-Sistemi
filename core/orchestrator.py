import time
from sim.rf_environment import RFEnvironment
from modules.detector.detector import WaterfallDetector
from modules.classifier.classifier import ModulationClassifier
from modules.direction_finder.df_logic import DirectionFinder
from modules.optimizer.et_optimizer import SmartOptimizer
from modules.tracker.kalman_tracker import KalmanTracker
from core.config import NOISE_FLOOR
from core.blackbox import MissionLogger

class SystemOrchestrator:
    """Main brain of the system. Routes data between modules."""
    
    def __init__(self):
        self.env = RFEnvironment()
        self.detector = WaterfallDetector()
        self.classifier = ModulationClassifier()
        self.df = DirectionFinder()
        self.optimizer = SmartOptimizer()
        self.tracker = KalmanTracker()
        self.logger = MissionLogger("logs/mission_log.db")
        self.mode = "AUTO"
        self.manual_jam = False
        self.latest_results = {}

    def run_cycle(self):
        # 1. Capture Spectrum
        psd_frame = self.env.generate_spectrum_frame()
        
        # 2. Detect Signals
        detections = self.detector.detect(psd_frame, NOISE_FLOOR)
        
        # 3. Process Detections & Update EA Strategy
        processed_signals = []
        for det in detections:
            mod_type = self.classifier.classify(det)
            aoa = self.df.estimate_aoa(det)
            
            # Match detected signal with the physical env signal to extract hardware imperfections
            matched_env_sig = None
            min_diff = float('inf')
            # Calculate approx physical frequency from index
            det_freq = (det['center_idx'] / self.env.fft_size) * self.env.fs + (self.env.center_freq - self.env.fs/2)
            
            for env_sig in self.env.active_signals:
                diff = abs(env_sig['freq'] - det_freq)
                if diff < min_diff:
                    min_diff = diff
                    matched_env_sig = env_sig
                    
            rfi_hash = "UNKNOWN"
            if matched_env_sig and min_diff < (self.env.fs * 0.05): # Check if match is close enough
                rfi_hash = self.classifier.extract_rfi_signature(matched_env_sig.get('phase_noise', 0), matched_env_sig.get('carrier_offset', 0))

            processed_signals.append({
                "freq_idx": det['center_idx'],
                "snr": round(det['snr'], 2),
                "type": mod_type,
                "aoa": round(aoa, 2),
                "rfi_hash": rfi_hash
            })
            
        # TRACKER UPDATE (Assigning Track IDs)
        processed_signals = self.tracker.update(processed_signals)
            
        # 4. AI Reinforcement Learning / Look-Through Logic or Manual Override
        if self.mode == "AUTO":
            ea_status = self.optimizer.update_strategy(processed_signals)
        else:
            ea_status = {
                "is_jamming": self.manual_jam,
                "status": "MANUAL - TAARRUZ (JAMMING)" if self.manual_jam else "MANUAL - STANDBY",
                "target_count": len(processed_signals),
                "reward": self.optimizer.total_reward, # Keep the last known reward UI
                "latest_reward_delta": 0
            }
            
        # 5. Log Events to Blackbox
        self.logger.log_signals(processed_signals)
        self.logger.log_action(ea_status)
            
        self.latest_results = {
            "waterfall": psd_frame,
            "signals": processed_signals,
            "ea_status": ea_status,
            "timestamp": time.time(),
            "sys_mode": self.mode
        }
        return self.latest_results

if __name__ == "__main__":
    orch = SystemOrchestrator()
    results = orch.run_cycle()
    print(f"Orchestrator run complete. Found {len(results['signals'])} signals.")
