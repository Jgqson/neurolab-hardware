from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VisaInstrument:
    address: str
    dry_run: bool = False

    def __post_init__(self) -> None:
        self._resource = None
        if not self.dry_run:
            import pyvisa

            rm = pyvisa.ResourceManager()
            self._resource = rm.open_resource(self.address)

    def write(self, cmd: str) -> None:
        if self.dry_run:
            print(f"[DRY-RUN][{self.address}] WRITE: {cmd}")
            return
        self._resource.write(cmd)

    def query(self, cmd: str) -> str:
        if self.dry_run:
            print(f"[DRY-RUN][{self.address}] QUERY: {cmd}")
            return "DRY_RUN"
        return str(self._resource.query(cmd)).strip()

    def close(self) -> None:
        if not self.dry_run and self._resource is not None:
            self._resource.close()


class SignalGenerator:
    def __init__(self, visa: VisaInstrument):
        self.visa = visa

    def reset(self) -> None:
        self.visa.write("*RST")
        self.visa.write("*CLS")

    def set_frequency(self, freq_hz: float) -> None:
        self.visa.write(f"FREQ {freq_hz}")

    def set_power(self, power_dbm: float) -> None:
        self.visa.write(f"POW {power_dbm}DBM")

    def output_on(self) -> None:
        self.visa.write("OUTP ON")

    def output_off(self) -> None:
        self.visa.write("OUTP OFF")

    def idn(self) -> str:
        return self.visa.query("*IDN?")
