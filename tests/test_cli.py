"""Tests for the chiptools_crc command-line interface."""

import json

import pytest

from chiptools_crc import CATALOG
from chiptools_crc.cli import main


def _write_dump(tmp_path, algo_name="CRC-32/BZIP2", endian="big"):
    algo = CATALOG[algo_name]
    payload = bytes(range(32))
    crc = algo.compute(payload)
    crc_bytes = (algo.width + 7) // 8
    data = payload + crc.to_bytes(crc_bytes, endian)
    path = tmp_path / "dump.bin"
    path.write_bytes(data)
    return path, algo, payload, crc


def test_list_all(capsys):
    rc = main(["list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "61 algorithms total." in out
    assert "CRC-32/BZIP2" in out
    assert "CRC-8/SMBUS" in out


def test_list_family(capsys):
    rc = main(["list", "--family", "CRC-32"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "CRC-32/ISO-HDLC" in out
    assert "CRC-16/ARC" not in out


def test_audit_coherent_exit_zero(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path)
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0:{len(payload)}"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "[OK ]" in out
    assert "COHERENT" in out


def test_audit_altered_exit_one(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path)
    raw = bytearray(path.read_bytes())
    raw[3] ^= 0xFF  # tamper a payload byte, leave stored CRC alone
    path.write_bytes(raw)
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0:{len(payload)}"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "[ALTERED]" in out
    assert "1 ALTERED REGION(S)" in out


def test_audit_literal_stored_hex(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path)
    # Provide the correct stored value inline -> OK.
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0:{len(payload)}:{crc:08x}"])
    assert capsys.readouterr().out.count("[OK ]") == 1
    assert rc == 0
    # Provide a wrong stored value inline -> ALTERED.
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0:{len(payload)}:deadbeef"])
    assert rc == 1


def test_audit_crc_at_explicit_offset(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path)
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0:{len(payload)}", "--crc-at", str(len(payload))])
    assert rc == 0
    assert "COHERENT" in capsys.readouterr().out


def test_audit_hex_offsets(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path)
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0x0:0x{len(payload):x}"])
    assert rc == 0


def test_audit_unknown_algo(tmp_path, capsys):
    path, *_ = _write_dump(tmp_path)
    rc = main(["audit", str(path), "--algo", "NOPE", "--region", "0:8"])
    assert rc == 2
    assert "unknown algo" in capsys.readouterr().err


def test_audit_json_coherent(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path)
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0:{len(payload)}", "--json"])
    report = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert report["verdict"] == "COHERENT"
    assert report["altered_count"] == 0
    assert report["algo"] == "CRC-32/BZIP2"
    region = report["regions"][0]
    assert region["status"] == "OK"
    assert region["consistent"] is True
    assert region["computed_hex"] == region["stored_hex"] == f"{crc:08x}"


def test_audit_json_altered(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path)
    raw = bytearray(path.read_bytes())
    raw[1] ^= 0x80
    path.write_bytes(raw)
    rc = main(["audit", str(path), "--algo", "CRC-32/BZIP2",
               "--region", f"0:{len(payload)}", "--json"])
    report = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert report["verdict"] == "ALTERED"
    assert report["altered_count"] == 1
    region = report["regions"][0]
    assert region["status"] == "ALTERED"
    assert region["consistent"] is False
    assert region["computed_hex"] != region["stored_hex"]


def test_audit_little_endian(tmp_path, capsys):
    path, algo, payload, crc = _write_dump(tmp_path, "CRC-16/MODBUS", "little")
    rc = main(["audit", str(path), "--algo", "CRC-16/MODBUS",
               "--region", f"0:{len(payload)}", "--endian", "little"])
    assert rc == 0
