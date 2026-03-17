import time
from sim.rf_environment import RFEnvironment
from modules.detector.detector import WaterfallDetector
from modules.classifier.classifier import ModulationClassifier
from modules.direction_finder.df_logic import DirectionFinder
from modules.optimizer.et_optimizer import SmartOptimizer
from core.config import NOISE_FLOOR

class SystemOrchestrator:
    """Main brain of the system. Routes data between modules."""
    
    def __init__(self):
        self.env = RFEnvironment()
        self.detector = WaterfallDetector()
        self.classifier = ModulationClassifier()
        self.df = DirectionFinder()
        self.optimizer = SmartOptimizer()
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
            processed_signals.append({
                "freq_idx": det['center_idx'],
                "snr": round(det['snr'], 2),
                "type": mod_type,
                "aoa": round(aoa, 2)
            })
            
        # 4. AI Reinforcement Learning / Look-Through Logic
        ea_status = self.optimizer.update_strategy(processed_signals)
            
        self.latest_results = {
            "waterfall": psd_frame,
            "signals": processed_signals,
            "ea_status": ea_status,
            "timestamp": time.time()
        }
        return self.latest_results

if __name__ == "__main__":
    orch = SystemOrchestrator()
    results = orch.run_cycle()
    print(f"Orchestrator run complete. Found {len(results['signals'])} signals.")
