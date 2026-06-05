"""Read-only integrity auditing.

``verify_integrity`` recomputes the checksum over one or more regions of a
dump and compares it against the value stored in the dump. A mismatch is
objective evidence that a region was edited *without* a consistent checksum
recompute, i.e. that the dump was altered at some point.

This module is deliberately read-only: it reports, it never writes a corrected
checksum back. It is an audit instrument, not an editor. The caller must supply
the algorithm (a :class:`~chiptools_crc.crc.Crc` instance) and the region
layout; nothing here is specific to any particular firmware.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal

from .crc import Crc, Sum

Endian = Literal["big", "little"]


@dataclass(frozen=True)
class Region:
    """Describes one checksum-protected region of a dump.

    data_start / data_len  - the byte range the checksum is computed over
    crc_start  / crc_len   - where the stored checksum lives, and its size
    endian                 - byte order of the stored checksum
    """

    name: str
    data_start: int
    data_len: int
    crc_start: int
    crc_len: int
    endian: Endian = "big"


@dataclass(frozen=True)
class RegionResult:
    name: str
    stored: int
    computed: int

    @property
    def consistent(self) -> bool:
        return self.stored == self.computed

    def __str__(self) -> str:
        status = "OK " if self.consistent else "ALTERED"
        return (
            f"[{status}] {self.name}: "
            f"stored=0x{self.stored:X} computed=0x{self.computed:X}"
        )


@dataclass(frozen=True)
class IntegrityReport:
    results: List[RegionResult] = field(default_factory=list)

    @property
    def consistent(self) -> bool:
        """True only if every region's stored checksum matches."""
        return all(r.consistent for r in self.results)

    @property
    def altered(self) -> List[RegionResult]:
        """Regions whose stored checksum does not match — evidence of editing."""
        return [r for r in self.results if not r.consistent]

    def __str__(self) -> str:
        lines = [str(r) for r in self.results]
        verdict = "COHERENT" if self.consistent else f"{len(self.altered)} ALTERED REGION(S)"
        lines.append(f"--- verdict: {verdict} ---")
        return "\n".join(lines)


def _read_int(data: bytes, off: int, length: int, endian: Endian) -> int:
    chunk = data[off:off + length]
    if len(chunk) != length:
        raise ValueError(f"region checksum at offset {off} runs past end of data")
    return int.from_bytes(chunk, endian)


def verify_integrity(data: bytes, regions: List[Region], algo) -> IntegrityReport:
    """Audit ``data``: recompute each region's checksum and compare to stored.

    Returns an :class:`IntegrityReport`. ``report.consistent`` is True when the
    dump's stored checksums all match the recomputed values; ``report.altered``
    lists the regions that don't, which is the objective "this was edited"
    signal a workshop diagnostic needs.

    ``algo`` is any object with a ``compute(bytes) -> int`` method
    (:class:`~chiptools_crc.crc.Crc` or :class:`~chiptools_crc.crc.Sum`).
    """
    if not isinstance(algo, (Crc, Sum)) and not hasattr(algo, "compute"):
        raise TypeError("algo must provide a compute(bytes) -> int method")

    results: List[RegionResult] = []
    for r in regions:
        stored = _read_int(data, r.crc_start, r.crc_len, r.endian)
        computed = algo.compute(data[r.data_start:r.data_start + r.data_len])
        results.append(RegionResult(r.name, stored, computed))
    return IntegrityReport(results)
