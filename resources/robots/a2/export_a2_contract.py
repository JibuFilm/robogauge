"""Export the LOCKED A2 control contract -> a2_contract.json (the robogauge config SSOT).

WP2(b) "never hand-typed" rule: the robogauge A2 robot config reads its constants from this
JSON, which is generated PROGRAMMATICALLY from the Point Motion locked sources:
  - `tools/gear_sonic_fk/robot_config.py` (the A2 RobotConfig: kp/kd/effort/default_stand/
     action_scale/decimation/timestep/stand_base_z),
  - the A2 sensorized MJCF (the body the policy is trained/evaluated on).

Running this against the source repo regenerates the committed a2_contract.json. The robogauge
A2 config selftest (`a2_config.py --selftest`, ships in the fork) re-derives the same values from
robot_config.py and asserts the committed JSON matches — so a drift between the two repos is a
loud test failure, never a silent hand-typed divergence.

USAGE (run from the source repo, with gear_sonic_fk importable):
  PYTHONPATH=/Users/jibujin/Developer/PerceptionGame/tools/gear_sonic_fk \
      python3 export_a2_contract.py --out a2_contract.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build_contract() -> dict:
    import robot_config as rc  # from gear_sonic_fk (on PYTHONPATH)
    a2 = rc.A2
    # joint order as policy/action order (strip the _joint suffix for the obs layout name list)
    joints = list(a2.joints)
    return {
        "schema": "a2_robogauge_contract_v1",
        "robot_name": "a2",
        "source": "tools/gear_sonic_fk/robot_config.py::A2 (unitree_rl_mjlab deploy.yaml v0)",
        "num_observations": 45,        # 12-DoF proprio, same layout as go2 (3+3+3+12+12+12)
        "num_actions": 12,
        "joints": joints,
        "p_gains": list(a2.kp),        # robogauge MuJoCo PD stiffness (kp 100/100/150 per leg)
        "d_gains": list(a2.kd),        # damping (kd 4/4/6 per leg)
        "effort": list(a2.effort),     # |torque| limits 120/120/180
        "default_dof_pos": list(a2.default_stand),  # (-0.1,0.9,-1.8) L / (0.1,0.9,-1.8) R ...
        "action_scale": a2.action_scale,            # 0.25
        "decimation": a2.decimation,                # 4
        "timestep": a2.timestep,                    # 0.005 -> control_dt 0.02 (50 Hz)
        "control_dt": round(a2.timestep * a2.decimation, 6),
        "stand_base_z": a2.stand_base_z,            # 0.4
        "spawn_height": a2.stand_base_z,            # spawn at stand height
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=HERE / "a2_contract.json")
    args = ap.parse_args()
    contract = build_contract()
    args.out.write_text(json.dumps(contract, indent=2))
    print(f"[export_a2_contract] wrote {args.out}")
    print(json.dumps(contract, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
