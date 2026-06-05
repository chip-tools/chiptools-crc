"""Read-only integrity audit of a binary dump.

Builds a tiny in-memory dump (two CRC-32 protected blocks), audits it, then
tampers one byte and audits again to show the ALTERED detection.

Run:  python examples/audit_dump.py
"""

from chiptools_crc import CATALOG, Region, verify_integrity

ALGO = CATALOG["CRC-32/BZIP2"]


def build_dump() -> bytes:
    """Two 64-byte blocks, each followed by its big-endian CRC-32."""
    block_a = bytes(range(64))
    block_b = bytes(range(64, 128))
    return (
        block_a + ALGO.compute(block_a).to_bytes(4, "big")
        + block_b + ALGO.compute(block_b).to_bytes(4, "big")
    )


# Region(name, data_start, data_len, crc_start, crc_len, endian)
REGIONS = [
    Region("block_A", 0x00, 0x40, 0x40, 4, "big"),
    Region("block_B", 0x44, 0x40, 0x84, 4, "big"),
]


def main() -> None:
    dump = build_dump()

    print("== pristine dump ==")
    report = verify_integrity(dump, REGIONS, ALGO)
    print(report)
    print("consistent:", report.consistent)

    print("\n== after tampering one byte in block_B ==")
    tampered = bytearray(dump)
    tampered[0x50] ^= 0x01  # flip a bit inside block_B's data
    report = verify_integrity(bytes(tampered), REGIONS, ALGO)
    print(report)
    print("altered regions:", [r.name for r in report.altered])


if __name__ == "__main__":
    main()
