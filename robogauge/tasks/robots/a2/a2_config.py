# -*- coding: utf-8 -*-
"""A2 robot configuration for robogauge — constants LOADED, never hand-typed.

Point Motion EVAL PREP WP2(b). Every control constant (p_gains/d_gains/default_dof_pos/
action_scale/decimation/effort/spawn height) is read from `resources/robots/a2/a2_contract.json`,
which is generated PROGRAMMATICALLY from the locked source (`tools/gear_sonic_fk/robot_config.py`
via `export_a2_contract.py`). Nothing here is a typed-in number — the parity selftest
(`--selftest`) re-derives from robot_config.py and asserts the committed JSON matches. This is the
direct lesson from the action_scale harness bug (RUN 2's false freeze): a single wrong contract
constant silently halves authority and reads as "frozen", so the constants follow the policy's own
contract, transcribed by code and gated by a parity test.

A2 is 12-DoF with the IDENTICAL joint order and proprio obs layout as the go2 MoE-CTS policy
(3 ang_vel + 3 gravity + 3 cmd + 12 joint_pos_rel + 12 joint_vel_rel + 12 last_action = 45), so
the obs builder is reused from `Go2`. Per the IsaacLab port (PORT_AUDIT_GO2_RL_ROBOTLAB.md row 6),
the LAB lineage feeds the command observation UNSCALED ([1,1,1]); the A2 patha policy is trained
in that port, so `a2_lab` uses cmd scale [1,1,1] (the `A2LabConfig`). The plain `A2Config` keeps
the go2-style [2,2,0.25] cmd scale for completeness/A-B.
"""
import json
from pathlib import Path
from typing import Literal

from robogauge import ROBOGAUGE_ROOT_DIR
from robogauge.tasks.robots import RobotConfig

_CONTRACT_PATH = Path(ROBOGAUGE_ROOT_DIR) / "resources" / "robots" / "a2" / "a2_contract.json"


def load_a2_contract() -> dict:
    """The locked A2 control contract (generated from robot_config.py)."""
    with open(_CONTRACT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_C = load_a2_contract()


class A2Config(RobotConfig):
    robot_name = "a2"
    robot_class = "A2MoE"  # CTS MoE deploy artifact (tuple output) — same as go2_moe

    class assets:
        robot_xml = "{ROBOGAUGE_ROOT_DIR}/resources/robots/a2/a2.xml"
        robot_spawn_height = _C["spawn_height"]   # 0.4 (stand_base_z)
        foot_geom_names = ["FL", "FR", "RL", "RR"]

    class control(RobotConfig.control):
        device = "cpu"
        # the A2 patha jit deploy export (45-dim single frame, internal history). Overridden per
        # checkpoint via --model-path; a placeholder until a real A2 walker ships.
        model_path = "{ROBOGAUGE_ROOT_DIR}/resources/models/a2/a2_patha.pt"
        control_dt = _C["control_dt"]             # 0.02 (50 Hz)
        control_type = "P"
        support_goal: Literal["velocity", "position"] = "velocity"

        # MuJoCo joint PD gains — LOADED from the locked contract (kp 100/100/150, kd 4/4/6).
        p_gains = list(_C["p_gains"])
        d_gains = list(_C["d_gains"])

        num_observations = _C["num_observations"]   # 45
        num_actions = _C["num_actions"]             # 12

        default_dof_pos = list(_C["default_dof_pos"])  # A2 stand pose (hip signs OPPOSITE go2)

        mj2model_dof_indices = list(range(12))      # identity: MJCF joint order == policy order
        save_additional_output = False

        class scales(RobotConfig.control.scales):
            lin_vel = 2.0
            ang_vel = 0.25
            dof_pos = 1.0
            dof_vel = 0.05
            action = _C["action_scale"]              # 0.25
            cmd = [2.0, 2.0, 0.25]                    # go2-style (A-B baseline)

    class commands(RobotConfig.commands):
        lin_vel_x = [-1.0, 1.0]
        lin_vel_y = [-1.0, 1.0]
        lin_vel_z = None
        ang_vel_roll = None
        ang_vel_pitch = None
        ang_vel_yaw = [-2.0, 2.0]


class A2LabConfig(A2Config):
    """A2 patha (IsaacLab port lineage): command observation is UNSCALED ([1,1,1])."""

    class control(A2Config.control):
        class scales(A2Config.control.scales):
            cmd = [1.0, 1.0, 1.0]   # port feeds raw command obs (audit row 6)


class A2TerrainConfig(A2Config):
    """A2 config for terrain tasks (wave/stairs/slope/obstacle)."""

    class commands(A2Config.commands):
        lin_vel_x = [-1.0, 1.0]
        lin_vel_y = [-1.0, 1.0]
        ang_vel_yaw = [-1.5, 1.5]


class A2LabTerrainConfig(A2LabConfig, A2TerrainConfig):
    """A2 lab config for terrain tasks."""


class A2V5Config(A2LabConfig):
    """A2 V5 perceptive student (the A3 sensorium): 45 proprio + 512 A3 dome ranges = 557 obs.
    Lab cmd scale [1,1,1] (patha lineage); robot_class A2V5 appends the dome ranges; the jit is
    the 557->12 MoE student (single-frame in, internal 5-frame history). The default model is the
    seg-1 export — submits from the training run override it server-side."""
    robot_class = "A2V5"

    class control(A2LabConfig.control):
        num_observations = 557
        model_path = "{ROBOGAUGE_ROOT_DIR}/resources/models/a2/a2_v5.pt"


class A2V5TerrainConfig(A2V5Config, A2TerrainConfig):
    """A2 V5 config for terrain tasks (wave/stairs/slope/obstacle)."""


# ---------------------------------------------------------------------------------------------
# Parity selftest (G-E4) — re-derive from robot_config.py and assert the committed JSON matches.
# ---------------------------------------------------------------------------------------------
def selftest() -> int:
    """Diff a2_contract.json against the locked source (robot_config.py). Needs gear_sonic_fk on
    PYTHONPATH (the source repo); run from the source side, not in the robogauge container."""
    print("=" * 70)
    print("a2_config --selftest  (G-E4 contract parity: a2_contract.json vs robot_config.py::A2)")
    print("=" * 70)
    import robot_config as rc  # the LOCKED source of truth
    a2 = rc.A2
    c = load_a2_contract()

    checks = []

    def eq(name, got, want):
        ok = (list(got) == list(want)) if isinstance(want, (list, tuple)) else (got == want)
        checks.append(ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:22} json={got}  source={want}")
        return ok

    eq("joints", c["joints"], a2.joints)
    eq("p_gains", c["p_gains"], a2.kp)
    eq("d_gains", c["d_gains"], a2.kd)
    eq("effort", c["effort"], a2.effort)
    eq("default_dof_pos", c["default_dof_pos"], a2.default_stand)
    eq("action_scale", c["action_scale"], a2.action_scale)
    eq("decimation", c["decimation"], a2.decimation)
    eq("timestep", c["timestep"], a2.timestep)
    eq("stand_base_z", c["stand_base_z"], a2.stand_base_z)
    eq("num_observations", c["num_observations"], 45)
    eq("num_actions", c["num_actions"], 12)
    eq("control_dt", c["control_dt"], round(a2.timestep * a2.decimation, 6))

    # also assert the config classes actually picked up the loaded values
    cfg = A2LabConfig()
    eq("A2LabConfig.p_gains", cfg.control.p_gains, a2.kp)
    eq("A2LabConfig.default_dof_pos", cfg.control.default_dof_pos, a2.default_stand)
    eq("A2LabConfig.cmd_scale", cfg.control.scales.cmd, [1.0, 1.0, 1.0])
    eq("A2LabConfig.action_scale", cfg.control.scales.action, 0.25)

    ok = all(checks)
    print("-" * 70)
    print(f"G-E4 contract parity {'PASS' if ok else 'FAIL'}: {sum(checks)}/{len(checks)} fields "
          f"match robot_config.py::A2")
    return 0 if ok else 1


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        raise SystemExit(selftest())
    ap.error("pass --selftest")
