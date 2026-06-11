# -*- coding: utf-8 -*-
"""A2 flat-gauge task config.

The gauge/terrain/goals are robot-agnostic, so A2 reuses the go2 flat gauge config verbatim
(`Go2FlatGaugeConfig` already sets the velocity goals + the hip/thigh dof_limits monitoring,
which substring-match A2's joints identically). The robot identity is supplied at registration
time (A2LabConfig). This thin subclass exists so the A2 task tree mirrors the go2 one.
"""
from robogauge.tasks.custom.go2.go2_flat_task import Go2FlatGaugeConfig


class A2FlatGaugeConfig(Go2FlatGaugeConfig):
    pass
