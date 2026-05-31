"""
convert_flac_to_mp3.py

Converts all FLAC files under SOURCE_DIR to 320kbps MP3 under DEST_DIR,
mirroring the folder structure exactly.

Restart-safe: if the output .mp3 already exists, the file is skipped.
Stop and restart at any time — no duplicate work.

Requirements:
  - Python 3.6+
  - ffmpeg on PATH (https://ffmpeg.org/download.html)

Usage:
  python convert_flac_to_mp3.py

Edit SOURCE_DIR and DEST_DIR below before running.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

SOURCE_DIR = "/mnt/d/Torrents/Music"
DEST_DIR   = "/mnt/d/Torrents/Music_MP3"
BITRATE    = "320k"
LOG_FILE   = "/mnt/d/Torrents/Music_MP3/conversion.log"

# ── Helpers ──────────────────────────────────────────────────────────────────

def log(msg, logfile):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"
    print(line)
    logfile.write(line + "\n")
    logfile.flush()


def find_flac_files(source_dir):
    for root, _, files in os.walk(source_dir):
        for fname in files:
            if fname.lower().endswith(".flac"):
                yield Path(root) / fname


def dest_path(flac_path, source_dir, dest_dir):
    rel = flac_path.relative_to(source_dir)
    return Path(dest_dir) / rel.with_suffix(".mp3")


def convert(src, dst, bitrate, logfile):
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-i", str(src),
        "-ab", bitrate,
        "-map_metadata", "0",   # copy all tags
        "-id3v2_version", "3",  # broad compatibility
        str(dst),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"  ERROR: {result.stderr.strip()}", logfile)
        return False
    return True


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(DEST_DIR, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as logfile:
        log("=" * 60, logfile)
        log(f"Starting conversion  {SOURCE_DIR}  →  {DEST_DIR}", logfile)

        flac_files = list(find_flac_files(SOURCE_DIR))
        total      = len(flac_files)
        skipped    = 0
        converted  = 0
        errors     = 0

        log(f"Found {total} FLAC files", logfile)

        for i, src in enumerate(flac_files, 1):
            dst = dest_path(src, SOURCE_DIR, DEST_DIR)

            if dst.exists():
                skipped += 1
                continue  # already done — skip silently

            label = src.relative_to(SOURCE_DIR)
            log(f"[{i}/{total}]  {label}", logfile)

            ok = convert(src, dst, BITRATE, logfile)
            if ok:
                converted += 1
            else:
                errors += 1
                # Leave a zero-byte marker so you can grep the log for failures
                # The missing/zero-byte MP3 will be retried on next run
                if dst.exists() and dst.stat().st_size == 0:
                    dst.unlink()

        log("-" * 60, logfile)
        log(f"Done.  Converted: {converted}  Skipped: {skipped}  Errors: {errors}", logfile)


if __name__ == "__main__":
    main()
