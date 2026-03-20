import random
import numpy as np
from core.config import (RL_ALPHA, RL_GAMMA, RL_EPSILON_START, RL_EPSILON_MIN, 
                          RL_EPSILON_DECAY, RL_ACTIONS)

class SmartOptimizer:
    """
    Cognitive ET Strategy Optimizer.
    Now uses an expanded state-space (DQN-ready) including threat sequence predictions.
    """
    def __init__(self):
        self.q_table = {}
        self.alpha = RL_ALPHA
        self.gamma = RL_GAMMA
        self.epsilon = RL_EPSILON_START
        self.actions = RL_ACTIONS
        self.total_reward = 0
        self.episode_count = 0
        self.prev_state = None
        self.prev_action_idx = None
        
    def _get_state(self, signals):
        # Expanded state vector for Deep Learning compatibility
        if not signals: return "IDLE"
        
        # Feature extraction: Threat counts and prediction status
        crit_count = sum(1 for s in signals if s.get('threat_level') == 'CRITICAL')
        has_pred   = sum(1 for s in signals if 'predicted_next_mhz' in s)
        
        # Build state key (discretized for Q-table, but ready for Tensor conversion)
        state_key = f"C{crit_count}_P{has_pred}"
        return state_key

    def update_strategy(self, signals):
        self.episode_count += 1
        current_state = self._get_state(signals)
        
        # Exploration vs Exploitation
        if random.random() < self.epsilon:
            action_idx = random.randint(0, len(self.actions) - 1)
        else:
            action_idx = self._get_best_action(current_state)
            
        action = self.actions[action_idx]
        
        # Reward calculation: based on prediction accuracy and threat mitigation
        reward = self._calculate_reward(signals, action)
        self.total_reward += reward
        
        # Q-Learning update (Bellman)
        if self.prev_state is not None:
            old_q = self.q_table.get((self.prev_state, self.prev_action_idx), 0.0)
            next_max_q = max([self.q_table.get((current_state, a), 0.0) for a in range(len(self.actions))])
            new_q = old_q + self.alpha * (reward + self.gamma * next_max_q - old_q)
            self.q_table[(self.prev_state, self.prev_action_idx)] = new_q
            
        # Decay epsilon
        if self.epsilon > RL_EPSILON_MIN:
            self.epsilon *= RL_EPSILON_DECAY
            
        self.prev_state = current_state
        self.prev_action_idx = action_idx
        
        return {
            "action": action,
            "status": f"AI: {action}",
            "reward": round(self.total_reward, 1),
            "epsilon": round(self.epsilon, 3),
            "episode": self.episode_count,
            "target_count": len(signals)
        }

    def _get_best_action(self, state):
        qs = [self.q_table.get((state, a), 0.0) for a in range(len(self.actions))]
        return int(np.argmax(qs))

    def _calculate_reward(self, signals, action):
        if not signals:
            return 1.0 if action == "STANDBY" else -0.5
        
        # High reward for LOOK_THROUGH if signals are complex
        if action == "LOOK_THROUGH" and len(signals) > 2:
            return 15.0
        
        # High reward for jamming critical targets
        has_crit = any(s.get('threat_level') == 'CRITICAL' for s in signals)
        if has_crit and action in ["JAM_SPOT", "JAM_BARRAGE"]:
            return 25.0
            
        # Bonus for having signal predictions
        if any('predicted_next_mhz' in s for s in signals):
            return 5.0
            
        return -1.0
