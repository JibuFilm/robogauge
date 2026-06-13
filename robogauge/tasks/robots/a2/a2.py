# -*- coding: utf-8 -*-
"""A2 robot classes for robogauge.

A2 is 12-DoF with the IDENTICAL joint order and proprio observation layout as the go2 MoE-CTS
policy, so the observation builder and action mapping are inherited verbatim from `Go2`/`Go2MoE`
(no new obs code — the contract differences are entirely in the config constants, which load from
a2_contract.json). `A2` is the plain (single-tensor output) deploy class; `A2MoE` is the
CTS-MoE class whose jit returns `(action, (weights, latent))` — the A2 patha deploy artifact.
"""
from robogauge.tasks.robots.go2.go2 import Go2
from robogauge.tasks.robots.go2.go2_moe import Go2MoE
from robogauge.tasks.robots.a2.a2_config import A2Config


class A2(Go2):
    """Plain A2 (single-tensor jit output). Reuses go2's obs builder + action mapping."""
    def __init__(self, cfg: A2Config):
        super().__init__(cfg)


class A2MoE(Go2MoE):
    """A2 CTS-MoE (jit returns (action, (weights, latent))). Reuses go2_moe's get_action."""
    def __init__(self, cfg: A2Config):
        super().__init__(cfg)


class A2V5(A2MoE):
    """A2 V5 perceptive student: the 45-dim proprio obs (inherited from Go2) with the 512-ray A3
    dome sensorium appended -> 557. Reuses go2_moe's MoE get_action (jit returns (action, (...)),
    single-frame in / internal 5-frame history). The dome ranges occupy obs[45:557], matching the
    training obs layout (policy + single_obs gain the TRAILING dome_ranges term, 45 -> 557)."""

    def __init__(self, cfg):
        super().__init__(cfg)
        self._dome = None          # lazy: A3Ranges needs mj_model, first available on build

    def build_observation(self, sim_data, goal_data):
        obs = super().build_observation(sim_data, goal_data)   # [0:45]=proprio, [45:557]=0
        if self._dome is None:
            from robogauge.tasks.robots.a2.a3_ranges import A3Ranges
            self._dome = A3Ranges(sim_data.mj_model)
        obs[45:45 + self._dome.n_total] = self._dome.ranges(sim_data.mj_model, sim_data.mj_data)
        return obs

    def get_action(self, obs):
        """Robust to BOTH V5 jit export formats: the clean deploy export (`policy.pt`) returns a
        single action tensor; the full CTS export returns `(action, (weights, latent))`. Take
        out[0] for tuples, out otherwise — so the same task works whatever the training run
        submits."""
        import torch
        obs_tensor = torch.tensor(obs, dtype=torch.float32).unsqueeze(0).to(self.device)
        out = self.model(obs_tensor)
        action = out[0] if isinstance(out, tuple) else out
        action = action.detach().cpu().numpy().squeeze(0)[self.model2mj_idx]
        self.last_action = action
        target_dof_pos = action * self.action_scale + self.default_dof_pos
        return target_dof_pos, self.p_gains, self.d_gains, self.control_type
