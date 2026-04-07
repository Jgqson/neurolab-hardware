from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class VisaConfig:
    smcv100b: str
    sgt100a: str


@dataclass
class CommonConfig:
    center_frequency_hz: float
    modulation: str
    symbol_rate: float
    cable_loss_db: float
    settle_time_s: float
    sensitivity_step_db: float


@dataclass
class SensitivityConfig:
    start_power_dbm: float
    min_power_dbm: float
    ber_threshold: float


@dataclass
class AciConfig:
    wanted_power_dbm: float
    offsets_hz: list[float]
    start_interferer_dbm: float
    stop_interferer_dbm: float
    interferer_step_db: float
    ber_threshold: float


@dataclass
class OutputConfig:
    csv_path: str


@dataclass
class TestPlan:
    visa: VisaConfig
    common: CommonConfig
    sensitivity: SensitivityConfig
    aci: AciConfig
    output: OutputConfig


def _require(data: dict[str, Any], key: str) -> Any:
    if key not in data:
        raise KeyError(f"Missing required config key: {key}")
    return data[key]


def load_test_plan(path: str | Path) -> TestPlan:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    visa_raw = _require(raw, "visa")
    common_raw = _require(raw, "common")
    sens_raw = _require(raw, "sensitivity")
    aci_raw = _require(raw, "aci")
    out_raw = _require(raw, "output")

    return TestPlan(
        visa=VisaConfig(**visa_raw),
        common=CommonConfig(**common_raw),
        sensitivity=SensitivityConfig(**sens_raw),
        aci=AciConfig(**aci_raw),
        output=OutputConfig(**out_raw),
    )
