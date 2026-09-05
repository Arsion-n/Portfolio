#!/bin/bash
# Synology Task Scheduler → User-defined script
# 每日複製 data/ 去 backups/YYYY-MM-DD/
set -euo pipefail
ROOT="${LEDGER_ROOT:-/volume1/docker/ledger}"
STAMP="$(date +%F)"
DEST="${ROOT}/backups/${STAMP}"
mkdir -p "${DEST}"
cp -a "${ROOT}/data" "${DEST}/"
cp -a "${ROOT}/schema" "${DEST}/"
find "${ROOT}/backups" -mindepth 1 -maxdepth 1 -type d -mtime +90 -exec rm -rf {} +
