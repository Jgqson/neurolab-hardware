from __future__ import annotations

import csv
import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from .config import TestPlan
from .instruments import SignalGenerator

BerReader = Callable[[], float]


def default_ber_reader() -> float:
    """默认 BER 读取器（占位）。

    实际项目中建议替换为：
    - 串口读取 DUT 统计；
    - TCP API 读取 BER/PER；
    - 或实验室上位机接口。
    """
    return 0.0


def run_sensitivity_test(
    plan: TestPlan,
    wanted: SignalGenerator,
    ber_reader: BerReader,
) -> list[dict]:
    results: list[dict] = []

    wanted.set_frequency(plan.common.center_frequency_hz)
    wanted.output_on()

    power = plan.sensitivity.start_power_dbm
    while power >= plan.sensitivity.min_power_dbm:
        effective_power = power - plan.common.cable_loss_db
        wanted.set_power(power)
        time.sleep(plan.common.settle_time_s)
        ber = ber_reader()

        row = {
            "test": "sensitivity",
            "wanted_power_dbm": power,
            "effective_wanted_power_dbm": effective_power,
            "ber": ber,
            "pass": ber <= plan.sensitivity.ber_threshold,
        }
        results.append(row)

        if ber > plan.sensitivity.ber_threshold:
            break

        power -= plan.common.sensitivity_step_db

    wanted.output_off()
    return results


def run_aci_test(
    plan: TestPlan,
    wanted: SignalGenerator,
    interferer: SignalGenerator,
    ber_reader: BerReader,
) -> list[dict]:
    results: list[dict] = []

    wanted.set_frequency(plan.common.center_frequency_hz)
    wanted.set_power(plan.aci.wanted_power_dbm)
    wanted.output_on()

    for offset in plan.aci.offsets_hz:
        interferer.set_frequency(plan.common.center_frequency_hz + offset)
        interferer_power = plan.aci.start_interferer_dbm
        while interferer_power <= plan.aci.stop_interferer_dbm:
            interferer.set_power(interferer_power)
            interferer.output_on()
            time.sleep(plan.common.settle_time_s)

            ber = ber_reader()
            cnr = plan.aci.wanted_power_dbm - interferer_power

            row = {
                "test": "aci",
                "offset_hz": offset,
                "wanted_power_dbm": plan.aci.wanted_power_dbm,
                "interferer_power_dbm": interferer_power,
                "cnr_db": cnr,
                "ber": ber,
                "pass": ber <= plan.aci.ber_threshold,
            }
            results.append(row)

            if ber > plan.aci.ber_threshold:
                interferer.output_off()
                break

            interferer_power += plan.aci.interferer_step_db

        interferer.output_off()

    wanted.output_off()
    return results


def write_results(path: str | Path, rows: list[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    fieldnames = sorted({k for r in rows for k in r.keys()})
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def dump_plan_snapshot(path: str | Path, plan: TestPlan) -> None:
    snapshot = {
        "visa": asdict(plan.visa),
        "common": asdict(plan.common),
        "sensitivity": asdict(plan.sensitivity),
        "aci": asdict(plan.aci),
        "output": asdict(plan.output),
    }
    Path(path).write_text(str(snapshot), encoding="utf-8")
