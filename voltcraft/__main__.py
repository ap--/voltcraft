import argparse
import sys
from typing import List, Optional

from .pps import PPS


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Serial port")
    sub = parser.add_subparsers(dest="cmd", metavar="CMD")
    parser.set_defaults(cmd="status")
    sub.add_parser(
        "status",
        help="Print all status information (default)",
    )
    sub.add_parser(
        "on",
        help="Power on",
    )
    sub.add_parser(
        "off",
        help="Power off",
    )
    sub.add_parser(
        "read",
        help="Read and print voltage, current and CV/CC mode",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    opts = create_parser().parse_args(argv)
    pps = PPS(port=opts.port, reset=False)
    if opts.cmd == "status":
        sys.stdout.write(f"MODEL={pps.MODEL}\n")
        sys.stdout.write(f"IMAX={pps.IMAX}\n")
        sys.stdout.write(f"VMAX={pps.VMAX}\n")
        sys.stdout.write(f"IMULT={pps.IMULT}\n")
        sys.stdout.write(f"limits={pps.limits()}\n")
        sys.stdout.write(f"reading={pps.reading()}\n")
    elif opts.cmd == "off":
        pps.output(0)
    elif opts.cmd == "on":
        pps.output(1)
    elif opts.cmd == "read":
        sys.stdout.write(f"reading={pps.reading()}\n")
    else:
        raise ValueError(f"Bad command {opts.cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
