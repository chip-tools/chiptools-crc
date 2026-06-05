"""Command-line interface for chiptools_crc.

    python -m chiptools_crc list [--family CRC-16]
    python -m chiptools_crc audit FILE.bin --algo CRC-32/BZIP2 \
        --region START:LEN[:STORED_HEX] [--region ...] [--endian big|little]

The ``audit`` command is read-only: it recomputes checksums and reports
OK / ALTERED. It never writes anything back to the file.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional, Tuple

from .catalog import CATALOG, FAMILIES
from .integrity import Region, RegionResult, verify_integrity


def _parse_int(text: str) -> int:
    """Parse an integer in decimal or 0x-hex form."""
    return int(text, 0)


def _parse_region(spec: str) -> Tuple[int, int, Optional[int]]:
    """Parse 'START:LEN[:STORED_HEX]' -> (start, length, stored_or_None)."""
    parts = spec.split(":")
    if len(parts) not in (2, 3):
        raise argparse.ArgumentTypeError(
            f"region must be START:LEN[:STORED_HEX], got {spec!r}"
        )
    start = _parse_int(parts[0])
    length = _parse_int(parts[1])
    stored = int(parts[2], 16) if len(parts) == 3 and parts[2] else None
    if start < 0 or length <= 0:
        raise argparse.ArgumentTypeError(f"invalid START/LEN in {spec!r}")
    return start, length, stored


def cmd_list(args) -> int:
    families = [args.family] if args.family else list(FAMILIES)
    for fam in families:
        if fam not in FAMILIES:
            print(f"unknown family: {fam} (choose from {', '.join(FAMILIES)})",
                  file=sys.stderr)
            return 2
        print(f"# {fam}")
        for name in FAMILIES[fam]:
            m = CATALOG[name]
            digits = (m.width + 3) // 4
            chk = "----" if m.check is None else f"0x{m.check:0{digits}X}"
            print(f"  {name:22s} width={m.width:<2d} check={chk}")
    print(f"\n{len(CATALOG)} algorithms total.")
    return 0


def cmd_audit(args) -> int:
    if args.algo not in CATALOG:
        print(f"unknown algo: {args.algo} (use 'list' to see all)", file=sys.stderr)
        return 2
    algo = CATALOG[args.algo]
    crc_bytes = (algo.width + 7) // 8

    try:
        with open(args.file, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        print(f"cannot read {args.file}: {exc}", file=sys.stderr)
        return 2

    specs = [_parse_region(s) for s in args.region]
    file_stored = [s for s in specs if s[2] is None]
    if args.crc_at is not None and len(file_stored) > 1:
        print("--crc-at is ambiguous with more than one file-stored region",
              file=sys.stderr)
        return 2

    results: List[RegionResult] = []
    try:
        for start, length, stored in specs:
            name = f"region@0x{start:X}+0x{length:X}"
            if stored is not None:
                computed = algo.compute(data[start:start + length])
                results.append(RegionResult(name, stored, computed))
            else:
                crc_off = args.crc_at if args.crc_at is not None else start + length
                region = Region(name, start, length, crc_off, crc_bytes, args.endian)
                results.append(verify_integrity(data, [region], algo).results[0])
    except ValueError as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2

    altered = [r for r in results if not r.consistent]
    digits = (algo.width + 3) // 4

    if args.json:
        payload = {
            "file": args.file,
            "algo": args.algo,
            "regions": [
                {
                    "name": r.name,
                    "status": "OK" if r.consistent else "ALTERED",
                    "computed_hex": f"{r.computed:0{digits}x}",
                    "stored_hex": f"{r.stored:0{digits}x}",
                    "consistent": r.consistent,
                }
                for r in results
            ],
            "verdict": "COHERENT" if not altered else "ALTERED",
            "altered_count": len(altered),
        }
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            print(r)
        verdict = "COHERENT" if not altered else f"{len(altered)} ALTERED REGION(S)"
        print(f"--- verdict: {verdict} ---")
    return 1 if altered else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chiptools-crc",
        description="CRC catalog + read-only integrity audit for binary dumps.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list catalogue algorithms")
    p_list.add_argument("--family", choices=list(FAMILIES),
                        help="restrict to one family")
    p_list.set_defaults(func=cmd_list)

    p_audit = sub.add_parser("audit", help="recompute & verify stored checksums")
    p_audit.add_argument("file", help="binary dump to audit")
    p_audit.add_argument("--algo", required=True, metavar="NAME",
                         help="catalogue algorithm name (see 'list')")
    p_audit.add_argument("--region", required=True, action="append",
                         metavar="START:LEN[:STORED_HEX]",
                         help="region to check; repeatable. START/LEN accept 0x..")
    p_audit.add_argument("--endian", choices=["big", "little"], default="big",
                         help="byte order of the stored checksum (default: big)")
    p_audit.add_argument("--crc-at", type=_parse_int, default=None, metavar="OFF",
                         help="explicit offset of the stored checksum "
                              "(single region without STORED_HEX)")
    p_audit.add_argument("--json", action="store_true",
                         help="emit a JSON report instead of plain text")
    p_audit.set_defaults(func=cmd_audit)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
