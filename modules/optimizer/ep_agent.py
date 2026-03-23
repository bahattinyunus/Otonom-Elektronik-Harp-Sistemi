import random
import numpy as np
from core.config import EP_CHANNELS

class EPAgent:
    """
    Electronic Protection (EP) Agent.
    Learns to suggest frequency hops for friendly nodes to avoid jamming/interference.
    """
    def __init__(self):
        self.channels = EP_CHANNELS
        self.q_table = {} # (current_channel, interference_level) -> action
        self.learning_rate = 0.2
        self.discount_factor = 0.9
        self.epsilon = 0.1
        
        self.current_channel_idx = 0
        self.total_hops = 0
        self.security_index = 100.0 # 0-100%

    def get_interference_level(self, signals, channel_mhz):
        """Calculates interference level on a specific channel."""
        interference = 0.0
        for s in signals:
            # Check if any signal is too close to our channel
            dist = abs(s["freq_mhz"] - channel_mhz)
            if dist < 0.05: # 50kHz proximity
                # Higher threat level signals cause more interference
                impact = {"CRITICAL": 50, "HIGH": 30, "MEDIUM": 15, "LOW": 5}.get(s["threat_level"], 5)
                interference += impact * (1.0 - dist/0.05)
        
        return min(interference, 100.0)

    def decide_action(self, signals):
        """Decides whether to hop or stay on current channel."""
        current_mhz = self.channels[self.current_channel_idx]
        interf_level = self.get_interference_level(signals, current_mhz)
        
        # State: (channel_idx, rounded_interference)
        state = (self.current_channel_idx, int(interf_level // 10))
        
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0] # [STAY, HOP]

        # Epsilon-greedy
        if random.random() < self.epsilon:
            action = random.randint(0, 1)
        else:
            action = np.argmax(self.q_table[state])

        hop_required = False
        suggested_channel = current_mhz

        if action == 1 or interf_level > 60: # HOP
            # Simple heuristic: find channel with least interference
            best_ch_idx = self.current_channel_idx
            min_interf = interf_level
            
            for i, ch in enumerate(self.channels):
                if i == self.current_channel_idx: continue
                ch_interf = self.get_interference_level(signals, ch)
                if ch_interf < min_interf:
                    min_interf = ch_interf
                    best_ch_idx = i
            
            if best_ch_idx != self.current_channel_idx:
                self.current_channel_idx = best_ch_idx
                suggested_channel = self.channels[best_ch_idx]
                hop_required = True
                self.total_hops += 1

        # Update Security Index
        # Reward/Index calculation
        current_interf = self.get_interference_level(signals, self.channels[self.current_channel_idx])
        self.security_index = max(0.0, 100.0 - current_interf)
        
        # Simple Q-update (Reward is security index)
        # In a real system, we'd wait for the next state, but here we simplify
        reward = self.security_index / 10.0
        self.q_table[state][action] += self.learning_rate * (reward - self.q_table[state][action])

        return {
            "hop_required": hop_required,
            "current_channel": suggested_channel,
            "security_index": round(self.security_index, 1),
            "interference_level": round(interf_level, 1),
            "total_hops": self.total_hops,
            "status": "SECURE" if self.security_index > 70 else "VULNERABLE" if self.security_index > 40 else "JAMMED"
        }
