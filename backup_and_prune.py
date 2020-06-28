#!/usr/bin/env python3

from datetime import datetime, timezone
import os
import sqlite3
import subprocess
import sys

PATTERN = {
    "day": "%Y-%m-%d",
    "week": "%G-%V",
    "month": "%Y-%m",
    "year": "%Y",
}

DEFAULT_N = {"day": 7, "week": 4, "month": 12, "year": 5}
BACKUP_DATETIME_PATTERN = "%Y_%m_%d_%H_%M_%S"
PRUNE = True
VERBOSE = True


def main():
    backup_dir = "/backups"
    db_path = os.environ["DB_PATH"]
    rclone_remote = os.environ["RCLONE_REMOTE"]
    rclone_path = os.environ["RCLONE_PATH"]

    backup_db(db_path, backup_dir)
    prune_backups(backup_dir)
    rclone_sync(backup_dir, rclone_remote, rclone_path)


def backup_db(db_path, backup_path):
    now_datetime_str = datetime.now(timezone.utc).strftime(BACKUP_DATETIME_PATTERN)

    db_con = sqlite3.connect(db_path)
    backup_con = sqlite3.connect(
        os.path.join(backup_path, f"{os.path.basename(db_path)}.{now_datetime_str}.bak")
    )

    with backup_con:
        db_con.backup(backup_con, pages=1)

    db_con.close()
    backup_con.close()


def prune_backups(data_dir):
    data_dict = _get_data_dict(data_dir)

    keep_set = set()
    for delta in ["day", "week", "month", "year"]:
        keep_set = _get_keep_set(
            data_dict,
            keep_set=keep_set,
            delta=delta,
            n=_get_delta_from_env(delta, DEFAULT_N[delta]),
        )

    if VERBOSE:
        print(sorted(keep_set))
    if PRUNE:
        _prune(data_dir, keep_set)


def rclone_sync(data_dir, rclone_remote, rclone_path):
    subprocess.run(
        ["rclone", "sync", data_dir, f"{rclone_remote}:{rclone_path}", "--dry-run"]
    )


def _get_keep_set(data_dict, *, keep_set, delta, n):
    """Add the first n files to the keep_set in increments of delta."""
    pattern = PATTERN[delta]

    if n == 0:
        return keep_set

    last = None
    for date_str, file_path in sorted(data_dict.items(), reverse=True):
        period = date_str.strftime(pattern)
        if period != last:
            last = period
            keep_set.add(file_path)
            if len(keep_set) == n:
                break

    return keep_set


def _get_delta_from_env(delta, default):
    """Get delta_n from the environment, or return default."""
    return int(os.environ.get(f"{delta.upper()}_N", default))


def _prune(data_dir, keep_set):
    """Prune all files in the data_dir that are not in the keep_set.

    This will only walk files in the data_dir, it is not recursive.
    """
    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        if os.path.isfile(file_path) and file not in keep_set:
            os.remove(file_path)


def _get_data_dict(data_dir):
    data_dict = {}
    for file in os.listdir(data_dir):
        if os.path.isfile(os.path.join(data_dir, file)):
            # backups are filename.ext.DATETIME.bak
            date_str = file.split(".")[-2:-1][0]
            data_dict[datetime.strptime(date_str, BACKUP_DATETIME_PATTERN)] = file

    return data_dict


if __name__ == "__main__":
    main()
