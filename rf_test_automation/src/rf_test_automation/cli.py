from __future__ import annotations

import argparse

from .config import load_test_plan
from .instruments import SignalGenerator, VisaInstrument
from .procedures import (
    default_ber_reader,
    dump_plan_snapshot,
    run_aci_test,
    run_sensitivity_test,
    write_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SMCV100B + SGT100A 灵敏度与邻道干扰自动化测试"
    )
    parser.add_argument("--config", required=True, help="YAML 配置文件路径")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="不连接真实仪器，仅打印 SCPI 指令",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = load_test_plan(args.config)

    wanted_visa = VisaInstrument(plan.visa.smcv100b, dry_run=args.dry_run)
    interferer_visa = VisaInstrument(plan.visa.sgt100a, dry_run=args.dry_run)

    wanted = SignalGenerator(wanted_visa)
    interferer = SignalGenerator(interferer_visa)

    wanted.reset()
    interferer.reset()

    print("Wanted IDN:", wanted.idn())
    print("Interferer IDN:", interferer.idn())

    ber_reader = default_ber_reader

    sensitivity_rows = run_sensitivity_test(plan, wanted, ber_reader)
    aci_rows = run_aci_test(plan, wanted, interferer, ber_reader)
    all_rows = sensitivity_rows + aci_rows

    write_results(plan.output.csv_path, all_rows)
    dump_plan_snapshot("results/plan_snapshot.txt", plan)

    wanted_visa.close()
    interferer_visa.close()

    print(f"Done. {len(all_rows)} rows written to {plan.output.csv_path}")


if __name__ == "__main__":
    main()
