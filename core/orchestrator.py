import time
import numpy as np
from sim.rf_environment import RFEnvironment
from modules.detector.detector import WaterfallDetector
from modules.classifier.classifier import ModulationClassifier
from modules.direction_finder.df_logic import DirectionFinder
from modules.optimizer.et_optimizer import SmartOptimizer
from modules.tracker.kalman_tracker import KalmanTracker
from modules.denoiser.denoiser import SpectralDenoiser
from modules.predictor.hop_predictor import FrequencyHopPredictor
from core.config import NOISE_FLOOR
from core.blackbox import MissionLogger


class SystemOrchestrator:
    """Main brain of the system. Routes data between all processing modules."""

    def __init__(self):
        self.env        = RFEnvironment()
        self.detector   = WaterfallDetector()
        self.classifier = ModulationClassifier()
        self.df         = DirectionFinder()
        self.optimizer  = SmartOptimizer()
        self.tracker    = KalmanTracker()
        self.denoiser   = SpectralDenoiser()
        self.predictor  = FrequencyHopPredictor()
        self.logger     = MissionLogger("logs/mission_log.db")

        self.mode           = "AUTO"
        self.manual_jam     = False
        self.denoiser_on    = True
        self.latest_results = {}

    def _idx_to_mhz(self, freq_idx: int) -> float:
        freq_hz = (freq_idx / self.env.fft_size) * self.env.fs + (self.env.center_freq - self.env.fs / 2)
        return round(freq_hz / 1e6, 3)

    def run_cycle(self):
        psd_raw    = self.env.generate_spectrum_frame()
        hz_per_bin = self.env.fs / self.env.fft_size

        # Optional spectral denoiser; waterfall always shows raw PSD
        psd_proc   = self.denoiser.process(psd_raw) if self.denoiser_on else psd_raw
        detections = self.detector.detect(psd_proc, NOISE_FLOOR)

        processed_signals = []
        for det in detections:
            det["freq_mhz"] = self._idx_to_mhz(det["center_idx"])

            mod_type, confidence, threat_level = self.classifier.classify(det)
            aoa, df_confidence                 = self.df.estimate_aoa(det)

            # RFI fingerprinting against active simulation signals
            det_freq = det["freq_mhz"] * 1e6
            rfi_hash = "UNKNOWN"
            min_diff = float("inf")
            matched  = None
            for env_sig in self.env.active_signals:
                diff = abs(env_sig["freq"] - det_freq)
                if diff < min_diff:
                    min_diff = diff
                    matched  = env_sig
            if matched and min_diff < (self.env.fs * 0.05):
                rfi_hash = self.classifier.extract_rfi_signature(
                    matched.get("phase_noise", 0), matched.get("carrier_offset", 0)
                )

            processed_signals.append({
                "freq_idx":      det["center_idx"],
                "freq_mhz":      det["freq_mhz"],
                "bandwidth_hz":  round(det["bandwidth_idx"] * hz_per_bin),
                "snr":           round(det["snr"], 2),
                "type":          mod_type,
                "confidence":    confidence,
                "threat_level":  threat_level,
                "aoa":           aoa,
                "df_confidence": df_confidence,
                "rfi_hash":      rfi_hash,
            })

        processed_signals = self.tracker.update(processed_signals)

        # 4. Predict next hop for tracking targets
        for sig in processed_signals:
            track_id = sig.get("track_id")
            if track_id:
                # Predicting for all identified tracks, LSTM learns if it's hopping
                prediction = self.predictor.update_and_predict(track_id, sig["freq_mhz"])
                if prediction:
                    sig["predicted_next_mhz"] = round(float(prediction), 3)

        if self.mode == "AUTO":
            ea_status = self.optimizer.update_strategy(processed_signals)
            self.env.set_jamming(ea_status.get("action", "STANDBY"))
        else:
            is_jam    = self.manual_jam
            ea_status = {
                "is_jamming":          is_jam,
                "status":              "MANUEL - TAARRUZ" if is_jam else "MANUEL - BEKLEME",
                "action":              "JAM_SPOT" if is_jam else "STANDBY",
                "target_count":        len(processed_signals),
                "reward":              self.optimizer.total_reward,
                "latest_reward_delta": 0,
                "epsilon":             self.optimizer.epsilon,
                "episode":             self.optimizer.episode_count,
                "q_states":            len(self.optimizer.memory),
            }
            self.env.set_jamming("JAM_SPOT" if is_jam else "STANDBY")

        psd_arr  = np.array(psd_raw)
        occupied = int(np.sum(psd_arr > (NOISE_FLOOR + 15)))
        spectrum_stats = {
            "occupancy_pct": round(occupied / len(psd_arr) * 100, 1),
            "peak_pwr_dbm":  round(float(np.max(psd_arr)), 1),
            "active_sigs":   len(self.env.active_signals),
            "rf_source":     "UDP" if self.env._udp_active() else "LOCAL",
            "denoiser_on":   self.denoiser_on,
        }

        self.logger.log_signals(processed_signals)
        self.logger.log_action(ea_status)

        # Per-cycle threat counts for the UI summary bar
        threat_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for s in processed_signals:
            lvl = s.get("threat_level", "LOW")
            threat_counts[lvl] = threat_counts.get(lvl, 0) + 1

        self.latest_results = {
            "waterfall":      psd_raw,
            "signals":        processed_signals,
            "ea_status":      ea_status,
            "spectrum_stats": spectrum_stats,
            "threat_counts":  threat_counts,
            "timestamp":      time.time(),
            "sys_mode":       self.mode,
        }
        return self.latest_results


if __name__ == "__main__":
    orch    = SystemOrchestrator()
    results = orch.run_cycle()
    print(f"Orchestrator cycle OK. Signals: {len(results['signals'])}")
