from robogauge.utils.task_register import task_register
from robogauge.tasks.simulator.mujoco_config import MujocoConfig
from robogauge.tasks.robots import (
    RobotConfig,
    Go2Config,
    Go2LabConfig,
    Go2MoEConfig,
    Go2TerrainConfig,
    Go2LabTerrainConfig,
    Go2MoETerrainConfig,
    A2Config,
    A2LabConfig,
    A2TerrainConfig,
    A2LabTerrainConfig,
)
from robogauge.tasks.pipeline import BasePipeline
from robogauge.tasks.gauge import BaseGaugeConfig

from robogauge.tasks.custom.go2 import *
from robogauge.tasks.custom.a2 import *

# Register tasks: Task name format '<robot_model>.<terrain>'
task_register.register('base', BasePipeline, MujocoConfig, BaseGaugeConfig, RobotConfig)

# Go2 MLP
task_register.register('go2.flat', BasePipeline, MujocoConfig, Go2FlatGaugeConfig, Go2Config)
task_register.register('go2.slope_fd', BasePipeline, MujocoConfig, Go2SlopeForwardGaugeConfig, Go2TerrainConfig)
task_register.register('go2.slope_bd', BasePipeline, MujocoConfig, Go2SlopeBackwardGaugeConfig, Go2TerrainConfig)
task_register.register('go2.wave', BasePipeline, MujocoConfig, Go2WaveGaugeConfig, Go2TerrainConfig)
task_register.register('go2.stairs_fd', BasePipeline, MujocoConfig, Go2StairsForwardGaugeConfig, Go2TerrainConfig)
task_register.register('go2.stairs_bd', BasePipeline, MujocoConfig, Go2StairsBackwardGaugeConfig, Go2TerrainConfig)
task_register.register('go2.obstacle', BasePipeline, MujocoConfig, Go2ObstacleGaugeConfig, Go2TerrainConfig)

# Go2 MoE
task_register.register('go2_moe.flat', BasePipeline, MujocoConfig, Go2FlatGaugeConfig, Go2MoEConfig)
task_register.register('go2_moe.slope_fd', BasePipeline, MujocoConfig, Go2SlopeForwardGaugeConfig, Go2MoETerrainConfig)
task_register.register('go2_moe.slope_bd', BasePipeline, MujocoConfig, Go2SlopeBackwardGaugeConfig, Go2MoETerrainConfig)
task_register.register('go2_moe.wave', BasePipeline, MujocoConfig, Go2WaveGaugeConfig, Go2MoETerrainConfig)
task_register.register('go2_moe.stairs_fd', BasePipeline, MujocoConfig, Go2StairsForwardGaugeConfig, Go2MoETerrainConfig)
task_register.register('go2_moe.stairs_bd', BasePipeline, MujocoConfig, Go2StairsBackwardGaugeConfig, Go2MoETerrainConfig)
task_register.register('go2_moe.obstacle', BasePipeline, MujocoConfig, Go2ObstacleGaugeConfig, Go2MoETerrainConfig)

# Go2 Lab
task_register.register('go2_lab.flat', BasePipeline, MujocoConfig, Go2FlatGaugeConfig, Go2LabConfig)
task_register.register('go2_lab.slope_fd', BasePipeline, MujocoConfig, Go2SlopeForwardGaugeConfig, Go2LabTerrainConfig)
task_register.register('go2_lab.slope_bd', BasePipeline, MujocoConfig, Go2SlopeBackwardGaugeConfig, Go2LabTerrainConfig)
task_register.register('go2_lab.wave', BasePipeline, MujocoConfig, Go2WaveGaugeConfig, Go2LabTerrainConfig)
task_register.register('go2_lab.stairs_fd', BasePipeline, MujocoConfig, Go2StairsForwardGaugeConfig, Go2LabTerrainConfig)
task_register.register('go2_lab.stairs_bd', BasePipeline, MujocoConfig, Go2StairsBackwardGaugeConfig, Go2LabTerrainConfig)
task_register.register('go2_lab.obstacle', BasePipeline, MujocoConfig, Go2ObstacleGaugeConfig, Go2LabTerrainConfig)

# A2 Lab (Point Motion patha lineage — IsaacLab port, unscaled cmd obs). Constants loaded from
# a2_contract.json (parity-tested vs robot_config.py::A2). Gauge configs reused from go2 (robot-
# agnostic terrain); robot identity = A2LabConfig / A2LabTerrainConfig.
task_register.register('a2_lab.flat', BasePipeline, MujocoConfig, A2FlatGaugeConfig, A2LabConfig)
task_register.register('a2_lab.slope_fd', BasePipeline, MujocoConfig, A2SlopeForwardGaugeConfig, A2LabTerrainConfig)
task_register.register('a2_lab.slope_bd', BasePipeline, MujocoConfig, A2SlopeBackwardGaugeConfig, A2LabTerrainConfig)
task_register.register('a2_lab.wave', BasePipeline, MujocoConfig, A2WaveGaugeConfig, A2LabTerrainConfig)
task_register.register('a2_lab.stairs_fd', BasePipeline, MujocoConfig, A2StairsForwardGaugeConfig, A2LabTerrainConfig)
task_register.register('a2_lab.stairs_bd', BasePipeline, MujocoConfig, A2StairsBackwardGaugeConfig, A2LabTerrainConfig)
task_register.register('a2_lab.obstacle', BasePipeline, MujocoConfig, A2ObstacleGaugeConfig, A2LabTerrainConfig)

# A2 (go2-style scaled cmd obs — A/B baseline).
task_register.register('a2.flat', BasePipeline, MujocoConfig, A2FlatGaugeConfig, A2Config)
