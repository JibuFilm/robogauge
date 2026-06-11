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
