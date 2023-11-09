"""voltcraft.pps"""
from __future__ import annotations

import functools
import sys
from typing import Literal

import serial

# The model can be identified by the maximum voltage and maximum current.
# But this is probably one of the weirdest naming-schemes I've seen...
# It just doesn't really make sense...
PPS_MODELS = {
    (18.0, 10.0): "PPS11810",  # not confirmed yet
    (36.2, 07.0): "PPS11360",  # confirmed
    (60.0, 02.5): "PPS11603",  # not confirmed yet
    (18.2, 22.0): "PPS13610",  # confirmed by Yanuino 2021-12-29, ersekcs 2021-11-24
    (36.2, 12.0): "PPS16005",  # confirmed
    (60.0, 05.0): "PPS11815",  # not confirmed yet
    (18.2, 12.0): "PPS11810",  # added MB 2019-01-10
    (32.2, 21.5): "DPPS3220",  # added tykling 2019-03-26
    (32.2, 31.5): "DPPS3230",  # added cdleonard 2023-09-13
    (60.5, 11.0): "DPPS6010",
}

# Some models have a minimum voltage.
PPS_MIN_VOLTAGE = {
    "PPS11810": 0,  # not confirmed yet
    "PPS11360": 0.8,  # confirmed by michael-dauer 2023-11-08
    "PPS11603": 0,  # not confirmed yet
    "PPS13610": 0,  # not confirmed yet
    "PPS16005": 0.8,  # confirmed by jonathanlarochelle 2023-10-27
    "PPS11815": 0,  # not confirmed yet
    "DPPS3220": 0.8,  # confirmed by jonathanlarochelle 2023-10-27
    "DPPS3230": 0,  # not confirmed yet
    "DPPS6010": 0,  # not confirmed yet
}

PPS_TIMEOUT = 1.00


def _pps_debug(s: str, debug: bool = True) -> None:
    """debug printing for PPS"""
    if debug:
        sys.stdout.write(s)
        sys.stdout.flush()


# noinspection PyPep8Naming
class PPS:
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        reset: bool = True,
        prom: int | None = None,
        debug: bool = False,
    ):
        """PPS(port, reset, prom)

        Parameters
        ----------
        port : str
            default '/dev/ttyUSB0'
        reset : bool
            reset the voltage and current limit to 0, and disable the output
        prom : int
            default None, if set choose preset values from internal PROM 0,1,2
        debug : bool
            output debug messages
        """
        self._serial = serial.Serial(port, timeout=PPS_TIMEOUT)
        self._serial.flushInput()
        self._serial.flushOutput()
        self._debug = functools.partial(_pps_debug, debug=bool(debug))

        try:
            gmax = self._query("GMAX")
        except serial.SerialTimeoutException:
            raise RuntimeError("No Voltcraft PPS powersupply connected to %s" % port)
        else:
            self._imult = 100.0 if gmax == "362700" else 10.0
            self._vmax = int(gmax[0:3]) / 10.0
            self._imax = int(gmax[3:6]) / self._imult

        try:
            self._model = PPS_MODELS[(self._vmax, self._imax)]
        except KeyError:
            raise RuntimeError(
                "unknown Voltcraft PPS model with max V: {}, I: {}".format(
                    self._vmax, self._imax
                )
            )

        try:
            self._vmin = PPS_MIN_VOLTAGE[self._model]
        except KeyError:
            raise RuntimeError(f"unknown minimum voltage for Voltcraft {self._model}")

        if bool(reset):
            self.output(0)
            self.voltage(0)
            self.current(0)

        if prom is not None:
            self.use_preset(prom)

    @property
    def VMAX(self) -> float:
        """maximum output voltage"""
        return self._vmax

    @property
    def IMAX(self) -> float:
        """maximum output current"""
        return self._imax

    @property
    def VMIN(self) -> float:
        """minimum output voltage"""
        return self._vmin

    @property
    def MODEL(self) -> str:
        """PS model number"""
        return self._model

    @property
    def IMULT(self) -> float:
        """current multiplier"""
        return self._imult

    def _query(self, cmd: str) -> str:
        """tx/rx to/from PS"""
        self._debug("PPS <- %s<CR>\n" % cmd)
        self._serial.write((cmd + "\r").encode())
        b: list[bytes] = []
        self._debug("PPS -> ")
        while True:
            b.append(self._serial.read(1))
            self._debug(b[-1].replace(b"\r", b"<CR>").decode())
            if b[-1] in {b"", b"\x00"}:
                raise serial.SerialTimeoutException()
            if b"".join(b[-3:]) == b"OK\r":
                break
        self._debug("\n")
        return (b"".join(b[:-4])).decode()

    def limits(self) -> tuple[float, float]:
        """get maximum voltage and current from PS"""
        return self._vmax, self._imax

    def output(self, state: int) -> None:
        """enable/disable the PS output"""
        state = 1 if not state else 0
        self._query("SOUT%d" % state)

    def voltage(self, voltage: float) -> None:
        """set voltage: silently saturates at VMIN and VMAX"""
        voltage = min(
            max(int(self._vmin * 10), int(voltage * 10)), int(self._vmax * 10)
        )
        self._query("VOLT%03d" % voltage)

    def current(self, current: float) -> None:
        """set current: silently saturates at 0 and IMAX"""
        current = min(max(0, int(current * self._imult)), int(self._imax * self._imult))
        self._query("CURR%03d" % current)

    def reading(self) -> tuple[float, float, Literal["CC", "CV"]]:
        """read applied output voltage and current and if PS is in "CV" or "CC" mode"""
        getd = self._query("GETD")
        voltage = int(getd[0:4]) / 100.0
        current = int(getd[4:8]) / 100.0
        mode: Literal["CC", "CV"] = "CC" if int(getd[8]) else "CV"
        return voltage, current, mode

    def store_presets(
        self,
        VC0: tuple[float, float],
        VC1: tuple[float, float],
        VC2: tuple[float, float],
    ) -> None:
        """
        store preset value tuples (voltage, current)
        """
        vcs: list[tuple[float, float]] = []
        for voltage, current in [VC0, VC1, VC2]:
            vcs.append(
                (
                    min(max(self._vmin, voltage), self._vmax) * 10,
                    min(max(0.0, current), self._imax) * self._imult,
                )
            )
        self._query("PROM%s" % "".join("%03d%03d" % s for s in vcs))

    def load_presets(self) -> list[tuple[float, float]]:
        """load preset value tuples (voltage, current)"""
        getm = self._query("GETM")
        v0 = int(getm[0:3]) / 10.0
        i0 = int(getm[3:6]) / self._imult
        v1 = int(getm[7:10]) / 10.0
        i1 = int(getm[10:13]) / self._imult
        v2 = int(getm[14:17]) / 10.0
        i2 = int(getm[17:20]) / self._imult
        return [(v0, i0), (v1, i1), (v2, i2)]

    def use_preset(self, nbr: int) -> None:
        """use specified preset"""
        nbr = min(max(0, int(nbr)), 2)
        self._query("RUNM%d" % nbr)

    @property
    def preset(self) -> tuple[float, float]:
        """preset values: (voltage, current)"""
        gets = self._query("GETS")
        voltage = int(gets[0:3]) / 10.0
        current = int(gets[3:6]) / self._imult
        return voltage, current

    @preset.setter
    def preset(self, VC: tuple[float, float]) -> None:
        self.preset_voltage = VC[0]
        self.preset_current = VC[1]

    @property
    def preset_voltage(self) -> float:
        """preset voltage"""
        govp = self._query("GOVP")
        voltage = int(govp[0:3]) / 10.0
        return voltage

    @preset_voltage.setter
    def preset_voltage(self, voltage: float) -> None:
        voltage = min(max(self._vmin, float(voltage)), self._vmax) * 10
        self._query("SOVP%03d" % int(voltage))

    @property
    def preset_current(self) -> float:
        """preset current"""
        gocp = self._query("GOCP")
        current = int(gocp[0:3]) / self._imult
        return current

    @preset_current.setter
    def preset_current(self, current: float) -> None:
        current = min(max(0.0, float(current)), self._imax) * self._imult
        self._query("SOCP%03d" % int(current))

    def power_dissipation(self) -> float:
        """return current power dissipation"""
        voltage, current, _ = self.reading()
        return voltage * current
