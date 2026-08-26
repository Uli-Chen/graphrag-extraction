#!/usr/bin/env python3
"""Repair invalid Mach-O zero-fill section offsets in installed extensions.

Some arm64 wheels contain S_ZEROFILL, S_GB_ZEROFILL, or
S_THREAD_LOCAL_ZEROFILL sections whose on-disk offset field is nonzero.  Newer
macOS dyld versions reject those binaries even though older releases ignored
the unused field.  This script scans thin 64-bit little-endian Mach-O extension
modules, optionally clears the invalid fields, and ad-hoc signs changed files.
"""

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path


MH_MAGIC_64 = 0xFEEDFACF
LC_SEGMENT_64 = 0x19
ZERO_FILL_SECTION_TYPES = {0x01, 0x0C, 0x12}


@dataclass(frozen=True)
class Violation:
    section_header_offset: int
    segment: str
    section: str
    section_type: int
    file_offset: int


def _name(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("ascii", errors="replace")


def violations(data: bytes) -> list[Violation]:
    if len(data) < 32 or struct.unpack_from("<I", data, 0)[0] != MH_MAGIC_64:
        return []

    ncmds = struct.unpack_from("<I", data, 16)[0]
    command_offset = 32
    found: list[Violation] = []
    for _ in range(ncmds):
        if command_offset + 8 > len(data):
            raise ValueError("truncated Mach-O load command")
        command, command_size = struct.unpack_from("<II", data, command_offset)
        if command_size < 8 or command_offset + command_size > len(data):
            raise ValueError("invalid Mach-O load command size")

        if command == LC_SEGMENT_64:
            if command_size < 72:
                raise ValueError("truncated LC_SEGMENT_64 command")
            segment = _name(data[command_offset + 8 : command_offset + 24])
            section_count = struct.unpack_from("<I", data, command_offset + 64)[0]
            section_offset = command_offset + 72
            if section_offset + 80 * section_count > command_offset + command_size:
                raise ValueError("section table exceeds LC_SEGMENT_64 command")
            for index in range(section_count):
                header = section_offset + 80 * index
                section = _name(data[header : header + 16])
                section_file_offset = struct.unpack_from("<I", data, header + 48)[0]
                flags = struct.unpack_from("<I", data, header + 64)[0]
                section_type = flags & 0xFF
                if (
                    section_type in ZERO_FILL_SECTION_TYPES
                    and section_file_offset != 0
                ):
                    found.append(
                        Violation(
                            section_header_offset=header,
                            segment=segment,
                            section=section,
                            section_type=section_type,
                            file_offset=section_file_offset,
                        )
                    )
        command_offset += command_size
    return found


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(".venv"))
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    candidates = sorted(root.rglob("*.so"))
    affected_files = 0
    affected_sections = 0

    for path in candidates:
        data = path.read_bytes()
        found = violations(data)
        if not found:
            continue
        affected_files += 1
        affected_sections += len(found)
        details = ", ".join(
            f"{item.segment}/{item.section}:0x{item.section_type:02x}@{item.file_offset}"
            for item in found
        )
        print(f"{path}: {details}")
        if not args.fix:
            continue

        if args.backup_dir is not None:
            relative = path.relative_to(root)
            backup = args.backup_dir.resolve() / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                shutil.copy2(path, backup)

        repaired = bytearray(data)
        for item in found:
            struct.pack_into("<I", repaired, item.section_header_offset + 48, 0)
        path.write_bytes(repaired)
        subprocess.run(
            ["codesign", "--force", "--sign", "-", "--timestamp=none", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        if violations(path.read_bytes()):
            raise RuntimeError(f"repair verification failed: {path}")

    action = "repaired" if args.fix else "found"
    print(
        f"{action} {affected_sections} invalid section(s) "
        f"across {affected_files} of {len(candidates)} extension module(s)"
    )
    if affected_files and not args.fix:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
