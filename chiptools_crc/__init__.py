"""chiptools_crc — generic CRC/checksum library + read-only integrity audit.

Public API:
    Crc, Sum            - parametric checksum engines
    CATALOG, FAMILIES   - standard Reveng models, keyed by name
    Region, verify_integrity, IntegrityReport - read-only tamper auditing
"""

from .catalog import CATALOG, FAMILIES
from .crc import Crc, Sum, reflect
from .integrity import IntegrityReport, Region, RegionResult, verify_integrity

__version__ = "0.1.1"

__all__ = [
    "Crc",
    "Sum",
    "reflect",
    "CATALOG",
    "FAMILIES",
    "Region",
    "RegionResult",
    "IntegrityReport",
    "verify_integrity",
    "__version__",
]
