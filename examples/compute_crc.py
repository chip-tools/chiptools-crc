"""Compute CRCs with a catalogue model and with a custom parameter set.

Run:  python examples/compute_crc.py
"""

from chiptools_crc import CATALOG, Crc

SAMPLE = b"123456789"


def main() -> None:
    # 1. Use a model straight from the catalogue, by canonical Reveng name.
    crc32 = CATALOG["CRC-32/ISO-HDLC"]
    print(f"CRC-32/ISO-HDLC({SAMPLE!r}) = 0x{crc32.compute(SAMPLE):08X}")
    print(f"  hex helper            = {crc32.compute_hex(SAMPLE)}")

    # 2. Define your own parametrisation (here: classic CRC-16/CCITT-FALSE).
    ccitt = Crc(width=16, poly=0x1021, init=0xFFFF,
                refin=False, refout=False, xorout=0x0000, name="CCITT-FALSE")
    print(f"{ccitt.name}({SAMPLE!r}) = 0x{ccitt.compute(SAMPLE):04X}")

    # 3. Browse a whole family.
    print("\nAll CRC-32 models in the catalogue:")
    for name in CATALOG:
        m = CATALOG[name]
        if name.startswith("CRC-32"):
            print(f"  {name:18s} check=0x{m.check:08X}")


if __name__ == "__main__":
    main()
