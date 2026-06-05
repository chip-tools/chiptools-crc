"""Generic parametric CRC / checksum engine (Williams / Rocksoft model).

The :class:`Crc` parameters match the Reveng catalogue exactly:

    width   - register width in bits
    poly    - generator polynomial (normal / MSB-first representation)
    init    - initial register value
    refin   - reflect each input byte (process LSB-first)
    refout  - reflect the final register before xorout
    xorout  - value XORed into the final register

This is a commodity implementation; it computes CRCs, it does not know or
care what the bytes mean.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


def reflect(value: int, width: int) -> int:
    """Reflect the low ``width`` bits of ``value``."""
    result = 0
    for i in range(width):
        if value & (1 << i):
            result |= 1 << (width - 1 - i)
    return result


@dataclass(frozen=True)
class Crc:
    """A fully-parametrised CRC algorithm.

    Instances are immutable and hashable, so they can live directly in the
    :data:`chiptools_crc.catalog.CATALOG` dictionary.
    """

    width: int
    poly: int
    init: int
    refin: bool
    refout: bool
    xorout: int
    name: str = ""
    check: Optional[int] = None  # published check value for b"123456789"

    @property
    def mask(self) -> int:
        return (1 << self.width) - 1

    def compute(self, data: bytes) -> int:
        """Compute the CRC of ``data`` (bit-by-bit reference implementation)."""
        width = self.width
        mask = self.mask
        topbit = 1 << (width - 1)
        poly = self.poly & mask
        crc = self.init & mask

        for byte in data:
            if self.refin:
                byte = reflect(byte, 8)
            # Align the byte to the top of the register.
            crc ^= (byte << (width - 8)) & mask if width >= 8 else (byte >> (8 - width))
            for _ in range(8):
                if crc & topbit:
                    crc = ((crc << 1) ^ poly) & mask
                else:
                    crc = (crc << 1) & mask

        if self.refout:
            crc = reflect(crc, width)
        return (crc ^ self.xorout) & mask

    def compute_hex(self, data: bytes) -> str:
        digits = (self.width + 3) // 4
        return f"{self.compute(data):0{digits}x}"

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"Crc(name={self.name!r}, width={self.width}, "
            f"poly=0x{self.poly:X}, init=0x{self.init:X}, "
            f"refin={self.refin}, refout={self.refout}, xorout=0x{self.xorout:X})"
        )


@dataclass(frozen=True)
class Sum:
    """A plain additive modular checksum (Reveng 'SUM' family).

    Provided for completeness; shares the ``compute`` / ``check`` interface
    with :class:`Crc` so both can coexist in the catalogue.
    """

    width: int
    init: int = 0
    name: str = ""
    check: Optional[int] = None

    @property
    def mask(self) -> int:
        return (1 << self.width) - 1

    def compute(self, data: bytes) -> int:
        return (self.init + sum(data)) & self.mask

    def compute_hex(self, data: bytes) -> str:
        digits = (self.width + 3) // 4
        return f"{self.compute(data):0{digits}x}"
