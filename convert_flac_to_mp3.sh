#!/usr/bin/env bash
#
# convert_flac_to_mp3.sh
#
# Converts all FLAC files under SOURCE_DIR to 320kbps MP3 under DEST_DIR,
# mirroring the folder structure exactly.
#
# Restart-safe: if the output .mp3 already exists it is skipped.
# Stop and restart at any time — no duplicate work.
#
# Requirements: ffmpeg on PATH
#
# Usage:
#   chmod +x convert_flac_to_mp3.sh
#   ./convert_flac_to_mp3.sh

SOURCE_DIR="/mnt/d/Torrents/Music"
DEST_DIR="/mnt/d/Torrents/Music_MP3"
BITRATE="320k"
LOG_FILE="$DEST_DIR/conversion.log"

# ── Setup ────────────────────────────────────────────────────────────────────

mkdir -p "$DEST_DIR"

log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S')  $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

# ── Collect files ────────────────────────────────────────────────────────────

mapfile -d '' FLAC_FILES < <(find "$SOURCE_DIR" -type f -iname "*.flac" -print0 | sort -z)
TOTAL=${#FLAC_FILES[@]}

log "$(printf '=%.0s' {1..60})"
log "Starting conversion  $SOURCE_DIR  →  $DEST_DIR"
log "Found $TOTAL FLAC files"

# ── Convert ──────────────────────────────────────────────────────────────────

CONVERTED=0
SKIPPED=0
ERRORS=0

for i in "${!FLAC_FILES[@]}"; do
    SRC="${FLAC_FILES[$i]}"
    NUM=$((i + 1))

    # Mirror path, swap extension
    REL="${SRC#$SOURCE_DIR/}"
    DST="$DEST_DIR/${REL%.flac}.mp3"
    DST="${DST%.FLAC}.mp3"   # handle uppercase .FLAC

    # Skip if already converted
    if [[ -f "$DST" ]]; then
        (( SKIPPED++ ))
        continue
    fi

    log "[$NUM/$TOTAL]  $REL"

    mkdir -p "$(dirname "$DST")"

    ffmpeg -hide_banner -loglevel error \
        -i "$SRC" \
        -ab "$BITRATE" \
        -map_metadata 0 \
        -id3v2_version 3 \
        "$DST"

    if [[ $? -eq 0 ]]; then
        (( CONVERTED++ ))
    else
        log "  ERROR converting: $REL"
        # Remove partial output so it gets retried on next run
        [[ -f "$DST" ]] && rm -f "$DST"
        (( ERRORS++ ))
    fi
done

# ── Summary ──────────────────────────────────────────────────────────────────

log "$(printf -- '-%.0s' {1..60})"
log "Done.  Converted: $CONVERTED  Skipped: $SKIPPED  Errors: $ERRORS"
