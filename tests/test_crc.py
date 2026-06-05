"""Tests for chiptools_crc.

The anchor test validates b"123456789" against 14 independently-known Reveng
check values (hard-coded here, not read from the catalogue), so a wrong
parameter in the catalogue cannot mask a wrong check value.
"""

import pytest

from chiptools_crc import CATALOG, Crc, Region, verify_integrity
from chiptools_crc.crc import reflect

SAMPLE = b"123456789"

# 14 canonical Reveng check values, independent of the catalogue.
KNOWN_CHECKS = {
    "CRC-8/SMBUS": 0xF4,
    "CRC-8/MAXIM-DOW": 0xA1,
    "CRC-8/DARC": 0x15,
    "CRC-16/ARC": 0xBB3D,
    "CRC-16/IBM-3740": 0x29B1,   # a.k.a. CCITT-FALSE
    "CRC-16/XMODEM": 0x31C3,
    "CRC-16/MODBUS": 0x4B37,
    "CRC-16/KERMIT": 0x2189,
    "CRC-16/USB": 0xB4C8,
    "CRC-16/IBM-SDLC": 0x906E,   # a.k.a. X-25
    "CRC-32/ISO-HDLC": 0xCBF43926,
    "CRC-32/BZIP2": 0xFC891918,
    "CRC-32/MPEG-2": 0x0376E6E7,
    "CRC-32/POSIX": 0x765E7680,
}


@pytest.mark.parametrize("name,expected", KNOWN_CHECKS.items())
def test_known_reveng_check_values(name, expected):
    assert CATALOG[name].compute(SAMPLE) == expected


@pytest.mark.parametrize("name", list(CATALOG))
def test_catalog_self_consistency(name):
    """Every catalogue entry computes its own published check value."""
    model = CATALOG[name]
    if model.check is not None:
        assert model.compute(SAMPLE) == model.check


def test_reflect():
    assert reflect(0x01, 8) == 0x80
    assert reflect(0x80, 8) == 0x01
    assert reflect(0b0000_0010, 8) == 0b0100_0000
    assert reflect(0x1234, 16) == 0x2C48


def test_compute_hex_width():
    assert CATALOG["CRC-32/ISO-HDLC"].compute_hex(SAMPLE) == "cbf43926"
    assert CATALOG["CRC-16/ARC"].compute_hex(SAMPLE) == "bb3d"
    assert CATALOG["CRC-8/SMBUS"].compute_hex(SAMPLE) == "f4"


def test_empty_input_returns_init_xorout():
    # CRC of empty data is just init (reflected) xor xorout.
    crc = Crc(16, 0x1021, 0xFFFF, False, False, 0x0000, name="t")
    assert crc.compute(b"") == 0xFFFF


# --- integrity audit --------------------------------------------------------

def _build_dump():
    """A tiny dump: 8 payload bytes followed by their big-endian CRC-32."""
    algo = CATALOG["CRC-32/ISO-HDLC"]
    payload = b"\x10\x20\x30\x40\x50\x60\x70\x80"
    crc = algo.compute(payload)
    return payload + crc.to_bytes(4, "big"), algo


def test_verify_integrity_coherent():
    dump, algo = _build_dump()
    regions = [Region("block0", 0, 8, 8, 4, "big")]
    report = verify_integrity(dump, regions, algo)
    assert report.consistent
    assert report.altered == []


def test_verify_integrity_detects_alteration():
    dump, algo = _build_dump()
    tampered = bytearray(dump)
    tampered[2] ^= 0xFF  # edit a payload byte, leave stored CRC untouched
    regions = [Region("block0", 0, 8, 8, 4, "big")]
    report = verify_integrity(bytes(tampered), regions, algo)
    assert not report.consistent
    assert [r.name for r in report.altered] == ["block0"]


def test_verify_integrity_little_endian():
    algo = CATALOG["CRC-16/MODBUS"]
    payload = b"\xde\xad\xbe\xef"
    dump = payload + algo.compute(payload).to_bytes(2, "little")
    regions = [Region("blk", 0, 4, 4, 2, "little")]
    assert verify_integrity(dump, regions, algo).consistent


def test_verify_integrity_out_of_range():
    with pytest.raises(ValueError):
        verify_integrity(b"\x00\x01", [Region("x", 0, 2, 2, 4, "big")],
                         CATALOG["CRC-32/ISO-HDLC"])
