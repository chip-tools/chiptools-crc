# chiptools_crc

[![CI](https://github.com/chip-tools/chiptools-crc/actions/workflows/ci.yml/badge.svg)](https://github.com/chip-tools/chiptools-crc/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/chiptools-crc.svg)](https://pypi.org/project/chiptools-crc/)

A small, dependency-free Python library for **CRC / checksum computation** and
**read-only integrity auditing** of binary dumps.

It provides:

- `Crc(width, poly, init, refin, refout, xorout)` — a fully parametric CRC
  engine following the Williams/Rocksoft (Reveng) model.
- `Sum(width, init)` — additive modular checksums (the Reveng `SUM` family).
- `CATALOG` — **61 standard, public Reveng models** keyed by canonical name
  (4 SUM + 20 CRC-8 + 30 CRC-16 + 7 CRC-32), each carrying its published
  check value.
- `verify_integrity(...)` — recomputes the checksums stored in a dump and
  reports which protected regions no longer match: an objective
  *"this dump was edited at some point"* signal for workshop diagnostics.

The catalogue contains **only standard, published algorithms**. There are no
firmware-specific "magic" constants and no checksum-forging / parameter-recovery
helpers: this library computes and *verifies* checksums, it does not re-sign
modified dumps.

## Install

```bash
pip install .                     # standard install (provides the CLI)
# or, just to run the test suite:
pip install -r requirements.txt
```

The library itself has no runtime dependencies (pure standard library).
Installing with pip also registers the `chiptools-crc` console command.

## Quick start — computing a CRC

```python
from chiptools_crc import CATALOG, Crc

# Use a catalogue model by name:
crc32 = CATALOG["CRC-32/ISO-HDLC"]
print(crc32.compute_hex(b"123456789"))   # -> cbf43926

# Or define your own parameter set:
mycrc = Crc(width=16, poly=0x1021, init=0xFFFF,
            refin=False, refout=False, xorout=0x0000, name="CCITT-FALSE")
print(hex(mycrc.compute(b"123456789")))  # -> 0x29b1
```

## Browsing the catalogue

```python
from chiptools_crc import CATALOG, FAMILIES

print(FAMILIES["CRC-16"])            # list of CRC-16 model names
for name in FAMILIES["CRC-32"]:
    m = CATALOG[name]
    print(f"{name:18s} check=0x{m.check:08X}")
```

## Integrity auditing (read-only)

`verify_integrity` answers one question objectively: *do the checksums stored
in this dump still match its contents?* If a region was edited in the past
without a consistent recompute, it shows up as `ALTERED`.

```python
from chiptools_crc import CATALOG, Region, verify_integrity

data = open("dump.bin", "rb").read()
algo = CATALOG["CRC-32/BZIP2"]

# Describe each checksum-protected region of the dump:
#   Region(name, data_start, data_len, crc_start, crc_len, endian)
regions = [
    Region("block_A", 0x0000, 0x1000, 0x1000, 4, "big"),
    Region("block_B", 0x1004, 0x0800, 0x1804, 4, "big"),
]

report = verify_integrity(data, regions, algo)
print(report)
# [OK ] block_A: stored=0x12AB34CD computed=0x12AB34CD
# [ALTERED] block_B: stored=0x00000000 computed=0x9F3C71A2
# --- verdict: 1 ALTERED REGION(S) ---

if not report.consistent:
    for r in report.altered:
        print("tampered region:", r.name)
```

`verify_integrity` never writes anything back; it only reports. The caller
supplies both the algorithm and the region layout, so the function is generic
and not tied to any particular firmware.

## Quick start (CLI)

The package installs a `chiptools-crc` command (equivalently
`python -m chiptools_crc`).

**List the catalogue:**

```bash
python -m chiptools_crc list
python -m chiptools_crc list --family CRC-32
#   CRC-32/ISO-HDLC        width=32 check=0xCBF43926
#   CRC-32/BZIP2           width=32 check=0xFC891918
#   ...
```

**Audit a dump** — `--region START:LEN[:STORED_HEX]`, repeatable. `START` and
`LEN` accept decimal or `0x..` hex.

```bash
# Stored checksum sits immediately after the region (the default convention):
python -m chiptools_crc audit dump.bin --algo CRC-32/BZIP2 --region 0:0x4000

# Several regions at once:
python -m chiptools_crc audit dump.bin --algo CRC-16/MODBUS \
    --region 0x0:0x1000 --region 0x1002:0x800 --endian little

# Compare against a stored value given inline (no read from the file):
python -m chiptools_crc audit dump.bin --algo CRC-32/BZIP2 --region 0:0x4000:cbf43926

# Stored checksum at an explicit offset:
python -m chiptools_crc audit dump.bin --algo CRC-32/BZIP2 --region 0:0x4000 --crc-at 0x7FFC
```

Output and exit code:

```text
[OK ] region@0x0+0x4000: stored=0x4342F70A computed=0x4342F70A
--- verdict: COHERENT ---
```

The command exits **0** when every region is coherent and **1** when at least
one region is `ALTERED`, so it drops straight into shell scripts and CI:

```bash
if ! chiptools-crc audit dump.bin --algo CRC-32/BZIP2 --region 0:0x4000; then
    echo "dump failed integrity audit"
fi
```

**Machine-readable output** with `--json` (handy for a workshop management
system or a CI step):

```bash
chiptools-crc audit dump.bin --algo CRC-32/BZIP2 \
    --region 0x0:0x40 --region 0x44:0x40 --json
```

```json
{
  "file": "dump.bin",
  "algo": "CRC-32/BZIP2",
  "regions": [
    {
      "name": "region@0x0+0x40",
      "status": "OK",
      "computed_hex": "4342f70a",
      "stored_hex": "4342f70a",
      "consistent": true
    },
    {
      "name": "region@0x44+0x40",
      "status": "ALTERED",
      "computed_hex": "0f8af635",
      "stored_hex": "00000000",
      "consistent": false
    }
  ],
  "verdict": "ALTERED",
  "altered_count": 1
}
```

The exit code is the same with `--json` (0 coherent / 1 altered).

## Audit use case in workshop diagnostics

A common diagnostic question, before any work is done on a module, is simply:
**"is this dump internally coherent, or was it edited at some point?"** That is
a yes/no question with an objective answer — and that answer is exactly what
`verify_integrity` / the `audit` command produce.

Typical workflow:

1. Read the module's contents to a `.bin` dump with your normal tool.
2. Know (from the module's documentation or your own reverse-engineering) which
   byte ranges are checksum-protected and where each checksum is stored.
3. Run an audit. Every region whose stored checksum still matches the recomputed
   value is reported `OK`; any region that does not is reported `ALTERED`.

```bash
chiptools-crc audit module_dump.bin --algo CRC-32/BZIP2 \
    --region 0x0000:0x4000 --region 0x4004:0x4000
```

An `ALTERED` verdict is objective evidence that a protected block was changed
without a consistent checksum recompute. That is useful for incoming inspection,
for documenting the state of a module before/after servicing, and for flagging
dumps that are not internally consistent.

Note on scope: this tool only **reports**. It does not recompute or write a
"corrected" checksum back into a dump — there is deliberately no write path and
no checksum-(re)signing helper here. It is an inspection instrument.

## Running the tests

```bash
python -m pytest -q
```

The suite validates `b"123456789"` against 14 independently hard-coded Reveng
check values, verifies the full catalogue is self-consistent, and exercises the
integrity-audit path (coherent dump, single-byte tamper detection, endianness,
bounds checking).

## Changelog

See [CHANGELOG.md](CHANGELOG.md). This is the initial `0.1.0` release.

## License

MIT — see [LICENSE](LICENSE).
