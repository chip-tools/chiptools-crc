"""Catalogue of standard Reveng CRC / checksum models.

Every entry is keyed by its canonical Reveng name and carries the published
``check`` value (the CRC of the ASCII string ``b"123456789"``), so the test
suite can validate the whole catalogue for self-consistency.

This catalogue intentionally contains ONLY public, standard algorithms.
"""

from __future__ import annotations

from typing import Union

from .crc import Crc, Sum

Model = Union[Crc, Sum]


def _c(
    name: str, width: int, poly: int, init: int,
    refin: bool, refout: bool, xorout: int, check: int,
) -> Crc:
    return Crc(width, poly, init, refin, refout, xorout, name=name, check=check)


# --- SUM (additive modular checksums) ---------------------------------------
_SUM = [
    Sum(8, 0, "SUM-8", check=0xDD),
    Sum(16, 0, "SUM-16", check=0x01DD),
    Sum(24, 0, "SUM-24", check=0x0001DD),
    Sum(32, 0, "SUM-32", check=0x000001DD),
]

# --- CRC-8 ------------------------------------------------------------------
_CRC8 = [
    _c("CRC-8/SMBUS", 8, 0x07, 0x00, False, False, 0x00, 0xF4),
    _c("CRC-8/CDMA2000", 8, 0x9B, 0xFF, False, False, 0x00, 0xDA),
    _c("CRC-8/DARC", 8, 0x39, 0x00, True, True, 0x00, 0x15),
    _c("CRC-8/DVB-S2", 8, 0xD5, 0x00, False, False, 0x00, 0xBC),
    _c("CRC-8/EBU", 8, 0x1D, 0xFF, True, True, 0x00, 0x97),
    _c("CRC-8/I-CODE", 8, 0x1D, 0xFD, False, False, 0x00, 0x7E),
    _c("CRC-8/I-432-1", 8, 0x07, 0x00, False, False, 0x55, 0xA1),
    _c("CRC-8/MAXIM-DOW", 8, 0x31, 0x00, True, True, 0x00, 0xA1),
    _c("CRC-8/ROHC", 8, 0x07, 0xFF, True, True, 0x00, 0xD0),
    _c("CRC-8/WCDMA", 8, 0x9B, 0x00, True, True, 0x00, 0x25),
    _c("CRC-8/BLUETOOTH", 8, 0xA7, 0x00, True, True, 0x00, 0x26),
    _c("CRC-8/GSM-A", 8, 0x1D, 0x00, False, False, 0x00, 0x37),
    _c("CRC-8/GSM-B", 8, 0x49, 0x00, False, False, 0xFF, 0x94),
    _c("CRC-8/HITAG", 8, 0x1D, 0xFF, False, False, 0x00, 0xB4),
    _c("CRC-8/LTE", 8, 0x9B, 0x00, False, False, 0x00, 0xEA),
    _c("CRC-8/MIFARE-MAD", 8, 0x1D, 0xC7, False, False, 0x00, 0x99),
    _c("CRC-8/NRSC-5", 8, 0x31, 0xFF, False, False, 0x00, 0xF7),
    _c("CRC-8/OPENSAFETY", 8, 0x2F, 0x00, False, False, 0x00, 0x3E),
    _c("CRC-8/SAE-J1850", 8, 0x1D, 0xFF, False, False, 0xFF, 0x4B),
    _c("CRC-8/AUTOSAR", 8, 0x2F, 0xFF, False, False, 0xFF, 0xDF),
]

# --- CRC-16 -----------------------------------------------------------------
_CRC16 = [
    _c("CRC-16/ARC", 16, 0x8005, 0x0000, True, True, 0x0000, 0xBB3D),
    _c("CRC-16/CDMA2000", 16, 0xC867, 0xFFFF, False, False, 0x0000, 0x4C06),
    _c("CRC-16/CMS", 16, 0x8005, 0xFFFF, False, False, 0x0000, 0xAEE7),
    _c("CRC-16/DDS-110", 16, 0x8005, 0x800D, False, False, 0x0000, 0x9ECF),
    _c("CRC-16/DECT-R", 16, 0x0589, 0x0000, False, False, 0x0001, 0x007E),
    _c("CRC-16/DECT-X", 16, 0x0589, 0x0000, False, False, 0x0000, 0x007F),
    _c("CRC-16/DNP", 16, 0x3D65, 0x0000, True, True, 0xFFFF, 0xEA82),
    _c("CRC-16/EN-13757", 16, 0x3D65, 0x0000, False, False, 0xFFFF, 0xC2B7),
    _c("CRC-16/GENIBUS", 16, 0x1021, 0xFFFF, False, False, 0xFFFF, 0xD64E),
    _c("CRC-16/GSM", 16, 0x1021, 0x0000, False, False, 0xFFFF, 0xCE3C),
    _c("CRC-16/IBM-3740", 16, 0x1021, 0xFFFF, False, False, 0x0000, 0x29B1),
    _c("CRC-16/IBM-SDLC", 16, 0x1021, 0xFFFF, True, True, 0xFFFF, 0x906E),
    _c("CRC-16/I-CODE", 16, 0x1021, 0xFFFF, False, False, 0x0000, 0x29B1),
    _c("CRC-16/KERMIT", 16, 0x1021, 0x0000, True, True, 0x0000, 0x2189),
    _c("CRC-16/LJ1200", 16, 0x6F63, 0x0000, False, False, 0x0000, 0xBDF4),
    _c("CRC-16/MAXIM-DOW", 16, 0x8005, 0x0000, True, True, 0xFFFF, 0x44C2),
    _c("CRC-16/MCRF4XX", 16, 0x1021, 0xFFFF, True, True, 0x0000, 0x6F91),
    _c("CRC-16/MODBUS", 16, 0x8005, 0xFFFF, True, True, 0x0000, 0x4B37),
    _c("CRC-16/NRSC-5", 16, 0x080B, 0xFFFF, True, True, 0x0000, 0xA066),
    _c("CRC-16/OPENSAFETY-A", 16, 0x5935, 0x0000, False, False, 0x0000, 0x5D38),
    _c("CRC-16/OPENSAFETY-B", 16, 0x755B, 0x0000, False, False, 0x0000, 0x20FE),
    _c("CRC-16/PROFIBUS", 16, 0x1DCF, 0xFFFF, False, False, 0xFFFF, 0xA819),
    _c("CRC-16/RIELLO", 16, 0x1021, 0xB2AA, True, True, 0x0000, 0x63D0),
    _c("CRC-16/SPI-FUJITSU", 16, 0x1021, 0x1D0F, False, False, 0x0000, 0xE5CC),
    _c("CRC-16/T10-DIF", 16, 0x8BB7, 0x0000, False, False, 0x0000, 0xD0DB),
    _c("CRC-16/TELEDISK", 16, 0xA097, 0x0000, False, False, 0x0000, 0x0FB3),
    _c("CRC-16/TMS37157", 16, 0x1021, 0x89EC, True, True, 0x0000, 0x26B1),
    _c("CRC-16/UMTS", 16, 0x8005, 0x0000, False, False, 0x0000, 0xFEE8),
    _c("CRC-16/USB", 16, 0x8005, 0xFFFF, True, True, 0xFFFF, 0xB4C8),
    _c("CRC-16/XMODEM", 16, 0x1021, 0x0000, False, False, 0x0000, 0x31C3),
]

# --- CRC-32 -----------------------------------------------------------------
_CRC32 = [
    _c("CRC-32/ISO-HDLC", 32, 0x04C11DB7, 0xFFFFFFFF, True, True, 0xFFFFFFFF, 0xCBF43926),
    _c("CRC-32/BZIP2", 32, 0x04C11DB7, 0xFFFFFFFF, False, False, 0xFFFFFFFF, 0xFC891918),
    _c("CRC-32/MPEG-2", 32, 0x04C11DB7, 0xFFFFFFFF, False, False, 0x00000000, 0x0376E6E7),
    _c("CRC-32/POSIX", 32, 0x04C11DB7, 0x00000000, False, False, 0xFFFFFFFF, 0x765E7680),
    _c("CRC-32/JAMCRC", 32, 0x04C11DB7, 0xFFFFFFFF, True, True, 0x00000000, 0x340BC6D9),
    _c("CRC-32C", 32, 0x1EDC6F41, 0xFFFFFFFF, True, True, 0xFFFFFFFF, 0xE3069283),
    _c("CRC-32/XFER", 32, 0x000000AF, 0x00000000, False, False, 0x00000000, 0xBD0BE338),
]


CATALOG: dict[str, Model] = {
    m.name: m for m in (_SUM + _CRC8 + _CRC16 + _CRC32)
}

# Convenience grouping used by the README / tests.
FAMILIES = {
    "SUM": [m.name for m in _SUM],
    "CRC-8": [m.name for m in _CRC8],
    "CRC-16": [m.name for m in _CRC16],
    "CRC-32": [m.name for m in _CRC32],
}
