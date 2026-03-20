import random
import json
import os
import ast
import numpy as np
from core.config import (RL_ALPHA, RL_GAMMA, RL_EPSILON_START, RL_EPSILON_MIN,
                          RL_EPSILON_DECAY, RL_ACTIONS)

class SmartOptimizer:
    """Q-Learning based Electronic Attack strategy optimizer."""

    def __init__(self):
        self.alpha = RL_ALPHA
        self.gamma = RL_GAMMA
        self.epsilon = RL_EPSILON_START
        self.epsilon_min = RL_EPSILON_MIN
        self.epsilon_decay = RL_EPSILON_DECAY
        self.actions = RL_ACTIONS
        self.n_actions = len(self.actions)

        self.q_table = {}
        self.q_table_path = "logs/q_table.json"

        self.total_reward = 0.0
        self.episode_count = 0
        self.last_state = None
        self.last_action_idx = None
        self.last_prev_count = 0

        self.jamming_active = False
        self.current_action = "STANDBY"
        self.status = "Bekleme - Pasif"

        self._load_q_table()

    def _discretize_state(self, detections):
        n = min(len(detections), 5)
        if detections:
            avg_snr = sum(d.get('snr', 0) for d in detections) / len(detections)
        else:
            avg_snr = 0
        snr_bucket = min(int(avg_snr / 15), 4)
        has_critical = int(any(d.get('threat_level', 'LOW') in ('HIGH', 'CRITICAL') for d in detections))
        return (n, snr_bucket, has_critical)

    def _get_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * self.n_actions
        return self.q_table[state]

    def _choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.n_actions)
        return int(np.argmax(self._get_q(state)))

    def _compute_reward(self, action_idx, prev_count, curr_count):
        action = self.actions[action_idx]
        if action in ("JAM_SPOT", "JAM_BARRAGE", "DECEPTIVE_JAM"):
            if curr_count < prev_count:
                return 10.0 * (prev_count - curr_count)
            elif curr_count == prev_count and prev_count > 0:
                return 1.5
            else:
                return -3.0
        elif action == "LOOK_THROUGH":
            return 1.0
        else:
            return 1.0 if prev_count == 0 else -4.0

    def update_strategy(self, current_detections):
        state = self._discretize_state(current_detections)

        if self.last_state is not None and self.last_action_idx is not None:
            reward = self._compute_reward(self.last_action_idx, self.last_prev_count, len(current_detections))
            q_vals = self._get_q(self.last_state)
            next_q_max = max(self._get_q(state))
            q_vals[self.last_action_idx] += self.alpha * (reward + self.gamma * next_q_max - q_vals[self.last_action_idx])
            self.total_reward += reward
            self.episode_count += 1
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
        else:
            reward = 0.0

        action_idx = self._choose_action(state)
        action = self.actions[action_idx]
        self.current_action = action
        self.last_state = state
        self.last_action_idx = action_idx
        self.last_prev_count = len(current_detections)
        self.jamming_active = action in ("JAM_SPOT", "JAM_BARRAGE", "DECEPTIVE_JAM")

        n_targets = len(current_detections)
        status_map = {
            "STANDBY":       "BEKLEME",
            "JAM_SPOT":      f"NOKTA TAARRUZ [{n_targets} Hedef]",
            "JAM_BARRAGE":   f"BARAJ TAARRUZ [{n_targets} Hedef]",
            "LOOK_THROUGH":  "BAK-GEC - Istihbarat",
            "DECEPTIVE_JAM": f"ALDAT.TAARRUZ [{n_targets} Hedef]",
        }
        self.status = status_map.get(action, action)

        if self.episode_count % 200 == 0 and self.episode_count > 0:
            self._save_q_table()

        return {
            "is_jamming": self.jamming_active,
            "status": self.status,
            "action": action,
            "target_count": n_targets,
            "reward": round(self.total_reward, 2),
            "latest_reward_delta": round(reward, 2),
            "epsilon": round(self.epsilon, 4),
            "episode": self.episode_count,
            "q_states": len(self.q_table),
        }

    def _save_q_table(self):
        try:
            os.makedirs(os.path.dirname(self.q_table_path) or ".", exist_ok=True)
            with open(self.q_table_path, 'w') as f:
                json.dump({str(k): v for k, v in self.q_table.items()}, f)
        except Exception:
            pass

    def _load_q_table(self):
        try:
            if os.path.exists(self.q_table_path):
                with open(self.q_table_path, 'r') as f:
                    data = json.load(f)
                self.q_table = {ast.literal_eval(k): v for k, v in data.items()}
        except Exception:
            pass
