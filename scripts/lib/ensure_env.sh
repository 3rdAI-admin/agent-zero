#!/usr/bin/env bash
# Keep a local backup of repo .env and restore it if it goes missing.

ensure_env_file() {
    local repo_root="$1"
    local env_file="$repo_root/.env"
    local backup_file="$repo_root/.env.backup"

    if [ -f "$env_file" ]; then
        if [ ! -f "$backup_file" ] || ! cmp -s "$env_file" "$backup_file"; then
            cp -p "$env_file" "$backup_file"
            chmod 600 "$backup_file" 2>/dev/null || true
            echo "[INFO] Synced .env backup -> .env.backup"
        fi
        return 0
    fi

    if [ -f "$backup_file" ]; then
        cp -p "$backup_file" "$env_file"
        chmod 600 "$env_file" 2>/dev/null || true
        echo "[WARN] Restored missing .env from .env.backup"
        return 0
    fi

    echo "[WARN] No .env or .env.backup found at repo root"
    return 0
}
