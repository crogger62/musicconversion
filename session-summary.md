# Music Library Conversion — Session Summary
*Date: 2026-05-30*

---

## Music Library Inventory

The library lives at `D:\Torrents\Music` and is organized as `Artist / Album / Tracks`.

| Metric | Value |
|---|---|
| Total size | 1.4 TB |
| Artists | 850 |
| Albums | 3,089 |
| Total audio tracks | 30,319 |

### Audio format breakdown

| Format | Files | Size |
|---|---|---|
| FLAC | 18,934 | 1,163 GB |
| MP3 | 11,363 | 120 GB |
| M4A | 22 | — |

FLAC accounts for ~85% of storage. Additional files in the library include cover art (7,791 images in JPG/PNG/GIF/TIF), plus rip artifacts: `.log`, `.cue`, `.nfo`, `.sfv`, `.m3u`.

---

## Library Analysis

### Mixed-format albums (FLAC + MP3 in same folder)
37 albums contain both FLAC and MP3 files. In most cases these are FLAC albums with 1–2 stray MP3s, likely bonus tracks or accidental additions. Notable exceptions are several Mastodon albums with up to 6 MP3s mixed in.

### MP3-only albums
735 albums contain MP3 files with no FLAC equivalent. These are predominantly older albums (pre-2010) acquired before lossless ripping became standard practice.

### Folder structure
Most albums are flat (tracks in the album folder). Two categories of subfolders exist:

- **608 folders** contain only artwork/scans/covers — no audio content
- **81 folders** are genuine multi-disc albums using `CD 1` / `CD 2` subdirectory conventions (e.g. limited editions, Japanese editions with bonus discs)

Any conversion script must recurse fully into all subdirectories to capture multi-disc albums.

---

## Conversion Plan

### Goal
Convert all FLAC files to MP3 for import into Apple Music, which has limited FLAC support.

### Parameters
| Setting | Value |
|---|---|
| Bitrate | 320 kbps CBR |
| Tag handling | Copy all metadata via `ffmpeg -map_metadata 0` |
| ID3 version | v2.3 (broadest Apple compatibility) |
| Output location | `D:\Torrents\Music_MP3\` mirroring source structure |
| Originals | Kept intact |

### Restart safety
The script checks whether the destination `.mp3` already exists before processing each file. If it does, the file is silently skipped. This makes the process fully idempotent — stop at any point, restart, and work already completed is not repeated.

Failed conversions remove any partial output file so they are automatically retried on the next run.

---

## Scripts

Both scripts live in `D:\Projects\MusicConversion\`.

### `convert_flac_to_mp3.py`

**Version 1 — Windows / PowerShell paths**
Uses Windows-style paths (`D:\Torrents\Music`). Invoke from PowerShell or Command Prompt:
```
python convert_flac_to_mp3.py
```

**Version 2 — WSL paths (current)**
Uses WSL-style paths (`/mnt/d/Torrents/Music`). Invoke from a WSL terminal:
```bash
python3 convert_flac_to_mp3.py
```

### `convert_flac_to_mp3.sh`

Bash implementation, WSL paths. Invoke from WSL:
```bash
chmod +x convert_flac_to_mp3.sh
./convert_flac_to_mp3.sh
```

Both scripts use `ffmpeg` as the underlying encoder. Verify it is available with `ffmpeg -version` before running.

---

## Suggested Improvements

### Logging
- The current log appends all runs to a single file (`conversion.log`). Consider timestamped log filenames per run (e.g. `conversion-2026-05-30.log`) to make it easier to review individual sessions.
- Add a count of remaining files at startup so you can estimate time to completion: `N files remaining (M already done)`.
- Pipe ffmpeg's `stderr` into the log on errors, not just a generic error message, so failed files are diagnosable without re-running manually.

### Output handling
- **Parallel encoding**: ffmpeg is single-threaded per file. Use Python's `concurrent.futures.ProcessPoolExecutor` or GNU `parallel` (bash) to run multiple conversions simultaneously, saturating multiple CPU cores and significantly reducing total runtime on a 19,000-file library.
- **Verification pass**: after conversion, check that the output MP3 is non-zero in size and can be opened by ffmpeg (`ffmpeg -v error -i file.mp3 -f null -`) to catch silently corrupted outputs.
- **Progress bar**: use `tqdm` (Python) or `pv` (bash) to show a live progress bar rather than a scrolling log, making long runs easier to monitor.
- **Dry-run mode**: add a `--dry-run` flag that prints what would be converted without actually doing it — useful for verifying the script sees all expected files before committing to a multi-hour job.
- **Summary report**: at the end of each run, write a machine-readable summary (JSON) alongside the log — total files, converted, skipped, errors, elapsed time — for easy parsing or comparison across runs.
