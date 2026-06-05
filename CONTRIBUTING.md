# Contributing to chiptools-crc

Thanks for your interest in improving the project. This is a small, focused
library; contributions that keep it simple and well-tested are very welcome.

## Scope

`chiptools-crc` is a **generic CRC/checksum library** plus a **read-only
integrity audit** tool. Two things are explicitly out of scope and will not be
merged:

- Firmware-specific "magic" constants in the catalogue. The catalogue contains
  only standard, published Reveng models.
- Any feature that writes a (re)computed checksum back into a dump, or that
  recovers a checksum parameter for the purpose of re-signing a modified dump.
  The audit path reports only; it has no write path by design.

New CRC models are welcome as long as they are standard, documented algorithms
and come with their published check value for `b"123456789"`.

## Development setup

```bash
git clone https://github.com/chip-tools/chiptools-crc.git
cd chiptools-crc
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e ".[test]"
```

## Running the tests

```bash
python -m pytest -q
```

Every catalogue entry is self-validated against its published check value, so a
new model with wrong parameters (or a wrong check value) will fail the suite.
Please add tests for any new behaviour.

## Adding a catalogue model

Add the entry to the appropriate family list in `chiptools_crc/catalog.py`:

```python
_c("CRC-16/EXAMPLE", 16, 0x1021, 0xFFFF, True, True, 0x0000, 0xABCD),
#   name             w   poly    init    refin refout xorout check
```

The `test_catalog_self_consistency` test will then verify that
`compute(b"123456789") == check` automatically.

## Style

- Pure standard library, no runtime dependencies.
- Keep public APIs type-annotated (the package ships `py.typed`).
- Match the surrounding code style; keep functions small and readable.

## Pull requests

1. Branch off `main`.
2. Make sure `python -m pytest -q` is green and `python -m build` succeeds.
3. Update `CHANGELOG.md` under `## [Unreleased]`.
4. Open the PR against `main`; CI runs the suite on Python 3.9–3.13.

By contributing you agree that your contributions are licensed under the
project's [MIT License](LICENSE).
