import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from core.config import (RL_ALPHA, RL_GAMMA, RL_EPSILON_START, RL_EPSILON_MIN, 
                          RL_EPSILON_DECAY, RL_ACTIONS)

class DQNNet(nn.Module):
    def __init__(self, input_size, num_actions):
        super(DQNNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, num_actions)
        )

    def forward(self, x):
        return self.net(x)

class SmartOptimizer:
    """
    Cognitive ET Strategy Optimizer.
    Uses an expanded state-space (DQN) including threat sequence predictions.
    """
    def __init__(self):
        self.actions = RL_ACTIONS
        self.state_size = 4 # [critical_count, high_count, has_pred, total_signals]
        
        # Hyperparameters
        self.gamma = RL_GAMMA
        self.epsilon = RL_EPSILON_START
        self.epsilon_min = RL_EPSILON_MIN
        self.epsilon_decay = RL_EPSILON_DECAY
        self.batch_size = 16
        
        # DQN Model Setup
        self.model = DQNNet(self.state_size, len(self.actions))
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.005)
        self.criterion = nn.MSELoss()
        
        # Experience Replay
        self.memory = deque(maxlen=2000)
        
        # Episode trackers
        self.total_reward = 0
        self.episode_count = 0
        self.prev_state = None
        self.prev_action_idx = None
        
    def _get_state(self, signals):
        # Convert signals mapping to numeric state vector for DQN
        if not signals: 
            return np.array([0, 0, 0, 0], dtype=np.float32)
        
        crit_count = sum(1 for s in signals if s.get('threat_level') == 'CRITICAL')
        high_count = sum(1 for s in signals if s.get('threat_level') == 'HIGH')
        has_pred   = 1 if any('predicted_next_mhz' in s for s in signals) else 0
        total      = len(signals)
        
        return np.array([crit_count, high_count, has_pred, total], dtype=np.float32)

    def remember(self, state, action_idx, reward, next_state):
        self.memory.append((state, action_idx, reward, next_state))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
            
        minibatch = random.sample(self.memory, self.batch_size)
        
        states = torch.tensor(np.array([m[0] for m in minibatch]), dtype=torch.float32)
        actions = torch.tensor([m[1] for m in minibatch], dtype=torch.long)
        rewards = torch.tensor([m[2] for m in minibatch], dtype=torch.float32)
        next_states = torch.tensor(np.array([m[3] for m in minibatch]), dtype=torch.float32)
        
        # Current Q values
        q_values = self.model(states)
        
        # Next Q values
        next_q_values = self.model(next_states).detach()
        max_next_q = next_q_values.max(1)[0]
        
        # Expected Q values using Bellman
        target_q_values = q_values.clone()
        for i in range(self.batch_size):
            target_q_values[i, actions[i]] = rewards[i] + self.gamma * max_next_q[i]
            
        loss = self.criterion(q_values, target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_strategy(self, signals, friendly_registry=None):
        self.episode_count += 1
        current_state = self._get_state(signals)
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            action_idx = random.randint(0, len(self.actions) - 1)
        else:
            state_tensor = torch.tensor(current_state, dtype=torch.float32).unsqueeze(0)
            self.model.eval()
            with torch.no_grad():
                q_values = self.model(state_tensor)
            self.model.train()
            action_idx = torch.argmax(q_values).item()
            
        action = self.actions[action_idx]
        
        # Measure reward based on system threat effectiveness
        reward = self._calculate_reward(signals, action, friendly_registry)
        self.total_reward += reward
        
        # Save memory and train network
        if self.prev_state is not None:
            self.remember(self.prev_state, self.prev_action_idx, reward, current_state)
            self.replay()
            
        # Decay exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        self.prev_state = current_state
        self.prev_action_idx = action_idx
        
        return {
            "action": action,
            "status": f"AI: {action}",
            "reward": round(self.total_reward, 1),
            "epsilon": round(self.epsilon, 3),
            "episode": self.episode_count,
            "target_count": len(signals),
            "q_states": len(self.memory)
        }

    def _calculate_reward(self, signals, action, friendly_registry=None):
        if not signals:
            return 2.0 if action == "STANDBY" else -1.5 
        
        crit_count = sum(1 for s in signals if s.get('threat_level') == 'CRITICAL')
        high_count = sum(1 for s in signals if s.get('threat_level') == 'HIGH')
        
        threat_reward = (crit_count * 20.0) + (high_count * 10.0)
        
        efficiency_penalty = 0
        if action == "JAM_BARRAGE" and len(signals) < 3:
            efficiency_penalty = -10.0
        
        energy_cost = {
            "STANDBY":      0.0,
            "LOOK_THROUGH": -0.5,
            "JAM_SPOT":     -2.0,
            "JAM_BARRAGE":  -5.0,
            "DECEPTIVE_JAM":-3.0,
            "DRFM_GHOSTS":  -4.0
        }.get(action, -1.0)

        intel_bonus = 5.0 if any('predicted_next_mhz' in s for s in signals) else 0.0

        # Collaborative Interference Avoidance (V1.2 Optimized)
        friendly_penalty = 0
        if friendly_registry:
            friendly_hashes = [node.get('rfi_hash') for node in friendly_registry]
            for s in signals:
                if s.get('rfi_hash') in friendly_hashes:
                    if action in ["JAM_SPOT", "JAM_BARRAGE"]:
                        friendly_penalty -= 50.0

        total_reward = threat_reward + energy_cost + efficiency_penalty + intel_bonus + friendly_penalty
        
        if action in ["JAM_SPOT", "JAM_BARRAGE", "DRFM_GHOSTS"] and (crit_count > 0 or high_count > 0):
            if friendly_penalty == 0: 
                total_reward += 10.0
            
        return total_reward
