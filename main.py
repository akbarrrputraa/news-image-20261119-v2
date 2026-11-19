# A working news-image-daily entry (Python 3.13, standard library only).
#
# The image is entry.png beside this file: "THE WORLD TODAY", a
# magazine-cover front page summing up Thursday 19 November 2026, drawn
# programmatically by render.py (kept in this repository) and checked by
# eye at full size and at 300 px. The program copies it to
# /output/entry.png, byte for byte, so the two runs the grader does write
# the same bytes. No network, no dependencies, no randomness.
#
# Before copying, it validates the image itself: PNG magic bytes, at most
# 1024x1024 pixels, at most 1 MiB — the competition's own limits — and it
# refuses to write a broken file. After the copy it re-reads both files and
# compares their SHA-256 digests, so a truncated or partial write can never
# pass silently.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_PIXELS = 1024
MAX_BYTES = 1_048_576


def png_size(data: bytes) -> tuple[int, int]:
    """Width and height from a PNG's IHDR chunk (bytes 16..24)."""
    if len(data) < 24 or data[:8] != PNG_MAGIC:
        raise ValueError("entry.png is not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


import binascii


def png_complete(data: bytes) -> bool:
    """Walk every PNG chunk, checking lengths and CRCs, and require IEND last.

    A trailing-bytes check alone can pass a file whose middle is corrupt;
    the chunk walk proves the file is whole: every chunk's declared length
    fits, its CRC matches, and the final chunk is IEND with nothing after it.
    """
    pos = 8  # skip the PNG magic
    seen_iend = False
    while pos + 8 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 8 + length + 4
        if end > len(data):
            return False
        chunk_crc = struct.unpack(">I", data[end - 4:end])[0]
        if binascii.crc32(data[pos + 4:end - 4]) & 0xFFFFFFFF != chunk_crc:
            return False
        seen_iend = ctype == b"IEND"
        pos = end
        if seen_iend:
            break
    return seen_iend and pos == len(data)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    data = source.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    width, height = png_size(data)
    if not png_complete(data):
        raise ValueError("entry.png is truncated or corrupt: chunk walk failed")
    if width > MAX_PIXELS or height > MAX_PIXELS:
        raise ValueError(f"entry.png is {width}x{height}, over the 1024x1024 limit")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    if sha256_file(source) != sha256_file(target):
        raise ValueError("copy verification failed: digests differ")
    print(f"entry.png: {width}x{height}, {len(data)} bytes, copied OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
