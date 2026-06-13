# -*- coding: utf-8 -*-
"""A3 dome range sensor for RoboGauge (the V5 perceptive student's 512-ray sensorium).

PORTED VERBATIM from Point Motion's `tools/gear_sonic_fk/a3_ranges_mj.py` (the train==deploy
pattern-parity counterpart). It loads the SAME `a3_pattern_contract_v1.json` the fork's RayCaster
+ kernel load, and casts the identical 512 rays (2 domes x 256, sensor-major [front, rear]) from
the identical lidar-frame sites with per-ray `mj_ray`. The RoboGauge a2 body IS the sensorized
body (make_a2_robot_xml.py builds it from a2_sensorized.xml) — same sites, same geom groups — so
the ranges match training by construction; `parity_a3_ranges.py` gates it to micrometers.

TRUE-FIRST-HIT is free: mj_ray sees terrain + the robot's own collision body. The one filter is
the visual-twin mask: render-only geoms (groups 2 + 4 = the 17 link visual meshes + the OS0 visual
proxies) are excluded; the physical body the sensor occludes against is the collision set (the
shapes the train-side kernel reimplements — G-V5-occ parity requires both sides see the same set).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from robogauge import ROBOGAUGE_ROOT_DIR

PATTERN_JSON = Path(ROBOGAUGE_ROOT_DIR) / "resources" / "robots" / "a2" / "a3_pattern_contract_v1.json"

# geom groups cast against: 0 (world/terrain/floor), 1, 3 (collision class), 5. EXCLUDED: 2 (link
# visual meshes), 4 (OS0 visual twins). uint8[6] — matches a2_moe_driver / a3_ranges_mj exactly.
GEOMGROUP_PHYSICAL = np.array([1, 1, 0, 1, 0, 1], dtype=np.uint8)


def load_pattern(path: str | Path = PATTERN_JSON) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        c = json.load(f)
    assert c.get("schema") == "a3_pattern_contract_v1", f"bad pattern schema in {path}"
    return c


def sensor_frame_directions_np(contract: dict) -> np.ndarray:
    return np.asarray(contract["directions_sensor_frame"], dtype=np.float64)


class A3Ranges:
    """The deployed sensorium: per-ray mj_ray over the contract pattern from the live site frames.

    Per-ray (not mj_multiRay): mujoco 3.9.0's ray-bundle pruning drops valid hits for rays far off
    the bundle mean when the pattern spans > a hemisphere (a2_ranges_mj finding 2026-06-12). At
    eval rates (1 env, 512 rays, 50 Hz) per-ray is ms-scale.
    """

    def __init__(self, mj_model, pattern_path: str | Path = PATTERN_JSON):
        import mujoco
        self._mujoco = mujoco
        self.contract = load_pattern(pattern_path)
        self.r_max = float(self.contract["r_max_m"])
        self.dirs_sensor = sensor_frame_directions_np(self.contract)        # (256, 3)
        self.n_per = self.dirs_sensor.shape[0]
        self.n_total = int(self.contract["total_rays"])                     # 512
        self.site_ids = [mj_model.site(s["site"]).id for s in self.contract["sensors"]]

    def raw_ranges(self, mj_model, mj_data) -> np.ndarray:
        """(512,) ray distances in meters; np.inf = no hit. Physical geoms only (visual groups
        2/4 masked); terrain + own body both visible = true-first-hit."""
        mujoco = self._mujoco
        out = np.full(self.n_total, np.inf)
        gid = np.zeros(1, dtype=np.int32)
        for k, sid in enumerate(self.site_ids):
            origin = np.array(mj_data.site_xpos[sid], dtype=np.float64)
            R = np.array(mj_data.site_xmat[sid], dtype=np.float64).reshape(3, 3)
            dirs_w = np.ascontiguousarray(self.dirs_sensor @ R.T)            # (256, 3)
            seg = out[k * self.n_per:(k + 1) * self.n_per]
            for i in range(self.n_per):
                dist = mujoco.mj_ray(mj_model, mj_data, origin, dirs_w[i],
                                     GEOMGROUP_PHYSICAL, 1, -1, gid)
                if gid[0] >= 0:
                    seg[i] = dist
        return out

    def ranges(self, mj_model, mj_data) -> np.ndarray:
        """(512,) normalized: clip(range / r_max, 0, 1); no-hit (inf) = 1.0."""
        r = self.raw_ranges(mj_model, mj_data)
        with np.errstate(invalid="ignore"):
            out = np.clip(r / self.r_max, 0.0, 1.0)
        out[~np.isfinite(r)] = 1.0
        return out.astype(np.float32)
