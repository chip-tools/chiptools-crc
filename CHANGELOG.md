# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `CONTRIBUTING.md` with development setup, test/PR workflow, and project scope.
- `examples/` directory with runnable usage scripts (`compute_crc.py`,
  `audit_dump.py`) and a short README.
- Ruff and mypy (strict) configuration, a `lint` extra, and a CI lint job.

### Changed

- Modernized type hints to PEP 585/604 built-in generics; added a
  `SupportsChecksum` protocol for the `verify_integrity` algorithm parameter.

## [0.1.0] - 2026-06-05

### Added

- **`Crc` engine** — fully parametric CRC following the Williams/Rocksoft
  (Reveng) model: `Crc(width, poly, init, refin, refout, xorout)` with
  `compute()` / `compute_hex()`.
- **`Sum` engine** — additive modular checksums (Reveng `SUM` family).
- **`CATALOG`** — 61 standard, public Reveng models keyed by canonical name
  (4 SUM + 20 CRC-8 + 30 CRC-16 + 7 CRC-32), each carrying its published
  check value for `b"123456789"`. `FAMILIES` groups them by family.
- **`verify_integrity`** — read-only integrity audit: recomputes the checksum
  over declared regions of a dump and reports `OK` / `ALTERED`. Reports only;
  it never writes a checksum back. Exposed via `Region`, `RegionResult`,
  `IntegrityReport`.
- **Command-line interface** (`chiptools-crc` / `python -m chiptools_crc`):
  - `list [--family ...]` — list catalogue algorithms with width and check value.
  - `audit FILE --algo NAME --region START:LEN[:STORED_HEX]` — audit a dump;
    repeatable `--region`, plus `--endian`, `--crc-at`, and `--json`. Exits 0
    when coherent, 1 when at least one region is `ALTERED`.
- **Packaging** — `pyproject.toml` for standard `pip install`, registering the
  `chiptools-crc` console script. Pure standard library, no runtime deps.
  Ships a `py.typed` marker (PEP 561) so downstream type checkers pick up the
  inline type hints.
- **Test suite** — pytest validating `b"123456789"` against 14 independently
  hard-coded Reveng check values, full-catalogue self-consistency, the
  integrity-audit path, and the CLI (text and JSON output).
- **Continuous integration** — GitHub Actions test matrix on Python 3.9–3.13
  for every push/PR, plus build + publish to PyPI via Trusted Publishing on
  `v*` tags.
- **Documentation** — README (with CI / PyPI / MIT badges) covering library,
  CLI, and workshop-audit usage; MIT license.
- **Repository config** — `.gitattributes` for consistent line-ending
  normalization and binary dump handling (`*.bin`, `*.eep`, `*.ori`, `*.e2p`).

[Unreleased]: https://github.com/chip-tools/chiptools-crc/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/chip-tools/chiptools-crc/releases/tag/v0.1.0
