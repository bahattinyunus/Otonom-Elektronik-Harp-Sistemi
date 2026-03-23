import time
from collections import deque

class MissionAnalyzer:
    """
    Cognitive Mission Intelligence Analyzer.
    Analyzes live system telemetry to generate human-readable strategic insights.
    """
    def __init__(self):
        self.history = deque(maxlen=50) # Last 50 cycles
        self.strategy_log = []
        self.last_report_time = 0
        self.report_interval = 5.0 # Seconds

    def update(self, latest_results):
        """Adds latest cycle data to history."""
        self.history.append(latest_results)

    def generate_strategic_summary(self):
        """Generates a text-based strategic summary of the mission."""
        if not self.history:
            return "SİSTEM BAŞLATILIYOR: Spektrum Gözlem Modu Aktif."

        now = time.time()
        # Only update summary at intervals to avoid flickering/noise
        # if now - self.last_report_time < self.report_interval:
        #     return self.strategy_log[-1] if self.strategy_log else "ANALİZ EDİLİYOR..."

        last_5 = list(self.history)[-5:]
        avg_threats = sum(len(h.get("signals", [])) for h in last_5) / len(last_5)
        
        # Detect patterns
        jamming_active = any(h.get("ea_status", {}).get("action") != "STANDBY" for h in last_5)
        heavy_threats = any(any(s.get("threat_level") in ["HIGH", "CRITICAL"] for s in h.get("signals", [])) for h in last_5)
        ep_hops = last_5[-1].get("ep_status", {}).get("total_hops", 0)
        security_idx = last_5[-1].get("ep_status", {}).get("security_index", 100.0)

        report = []
        
        # Operational Status
        if avg_threats == 0:
            report.append("SPEKTRUM TEMİZ: Kayda değer bir tehdit tespit edilmedi.")
        elif avg_threats < 2: report.append("DÜŞÜK YOĞUNLUKLU AKTİVİTE: Münferit sinyaller izleniyor.")
        else: report.append(f"YÜKSEK SPEKTRAL YOĞUNLUK: {int(avg_threats)} aktif hedef takip ediliyor.")

        # EA Logic
        if jamming_active:
            report.append("ELEKTRONİK TAARRUZ: AI Optimizer aktif karıştırma politikası uyguluyor.")
        
        # EP Logic
        if security_idx < 60:
            report.append(f"DİKKAT: Spektral Güvenlik Endeksi %{security_idx} - Yoğun girişim tespit edildi!")
        
        if heavy_threats:
            report.append("KRİTİK TEHDİT: LPI/Radar benzeri modülasyonlar tespit edildi, karşı tedbirler devrede.")

        if ep_hops > 0:
            report.append(f"OTONOM KORUNMA: EP Ajanı {ep_hops} adet başarılı frekans atlaması gerçekleştirdi.")

        # Final Summary selection
        summary = " | ".join(report)
        self.strategy_log.append(summary)
        self.last_report_time = now
        
        return summary

    def get_mission_metrics(self):
        """Calculates high-level mission KPIs."""
        if not self.history:
            return {"effectiveness": 0, "security": 100}
            
        success_count = sum(1 for h in self.history if h.get("ea_status", {}).get("reward", 0) > 0)
        effectiveness = (success_count / len(self.history)) * 100
        
        security = self.history[-1].get("ep_status", {}).get("security_index", 100.0)
        
        return {
            "effectiveness": round(effectiveness, 1),
            "security": round(security, 1)
        }
