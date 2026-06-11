# -*- coding: utf-8 -*-
from robogauge.tasks.custom.a2.a2_flat_task import A2FlatGaugeConfig

# Terrain gauge configs are robot-agnostic; A2 terrain tasks reuse the go2 terrain gauge configs
# (re-exported here so the a2 task registry block reads symmetrically with go2).
from robogauge.tasks.custom.go2 import (
    Go2SlopeForwardGaugeConfig as A2SlopeForwardGaugeConfig,
    Go2SlopeBackwardGaugeConfig as A2SlopeBackwardGaugeConfig,
    Go2WaveGaugeConfig as A2WaveGaugeConfig,
    Go2StairsForwardGaugeConfig as A2StairsForwardGaugeConfig,
    Go2StairsBackwardGaugeConfig as A2StairsBackwardGaugeConfig,
    Go2ObstacleGaugeConfig as A2ObstacleGaugeConfig,
)
