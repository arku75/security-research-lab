#!/usr/bin/env python3
"""Summarize local file metadata without emitting paths or reading contents."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import stat


EXTENSIONS = {
    "source": {".py", ".sh", ".ps1", ".bat", ".js", ".ts", ".tsx", ".jsx", ".rb", ".go", ".rs", ".c", ".cpp", ".h", ".java", ".php"},
    "documentation": {".md", ".rst", ".txt", ".pdf", ".docx", ".odt"},
    "structured_data": {".json", ".jsonl", ".csv", ".tsv", ".xml", ".yaml", ".yml", ".toml", ".ini"},
    "archive": {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"},
    "binary_or_model": {".bin", ".exe", ".dll", ".so", ".img", ".iso", ".gguf", ".safetensors", ".pt", ".onnx"},
    "media": {".png", ".jpg", ".jpeg", ".svg", ".webp", ".mp3", ".wav", ".mp4"},
}
KNOWN_EXTENSIONS = set().union(*EXTENSIONS.values())
SKIPPED_DIRECTORIES = {".git", ".venv", "venv", "node_modules", "__pycache__"}
REVIEW_NAME_CUES = ("password", "credential", "secret", "token", "cookie", "backup", "recovery", "session", "private", "account", "log", "combos")
LICENSE_NAMES = {"license", "licence", "license.md", "license.txt", "licence.md", "licence.txt", "copying", "notice", "notice.txt"}


def inventory(root, *, max_files=200000, max_entries=500000, max_depth=32):
    """Return aggregate metadata only; root names and exception text stay private.

    A changing or adversarial filesystem is outside the threat model. Symlink
    entries are skipped, but this is not an OS sandbox or a secret detector.
    """
    if not (1 <= max_files <= 200000 and 1 <= max_entries <= 500000 and 0 <= max_depth <= 64):
        raise ValueError("Inventory limits are outside the supported range.")
    report = {
        "status": "complete", "regular_files": 0, "directories_visited": 0,
        "entries_seen": 0, "regular_file_bytes": 0, "symlinks_skipped": 0,
        "special_entries_skipped": 0, "errors": 0, "depth_limited_directories": 0,
        "files_over_100_mib": 0, "license_name_candidates": 0,
        "names_requiring_private_review": 0, "stop_reason": None,
    }
    extension_counts, category_counts, excluded_counts = Counter(), Counter(), Counter()
    root = Path(root)
    try:
        mode = root.lstat().st_mode
        if not stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
            raise ValueError("The root must be an ordinary directory.")
    except (OSError, ValueError):
        report.update(status="unavailable", errors=1)
        return report
    stack = [(root, 0)]
    stopped = False
    while stack and not stopped:
        directory, depth = stack.pop()
        try:
            with os.scandir(directory) as entries:
                report["directories_visited"] += 1
                for entry in entries:
                    if report["entries_seen"] >= max_entries:
                        report.update(status="limited", stop_reason="entry_limit")
                        stopped = True
                        break
                    report["entries_seen"] += 1
                    try:
                        if entry.is_symlink():
                            report["symlinks_skipped"] += 1
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            if entry.name in SKIPPED_DIRECTORIES:
                                excluded_counts[entry.name] += 1
                            elif depth >= max_depth:
                                report["depth_limited_directories"] += 1
                            else:
                                stack.append((Path(entry.path), depth + 1))
                            continue
                        info = entry.stat(follow_symlinks=False)
                        if not stat.S_ISREG(info.st_mode):
                            report["special_entries_skipped"] += 1
                            continue
                        if report["regular_files"] >= max_files:
                            report.update(status="limited", stop_reason="file_limit")
                            stopped = True
                            break
                        name = entry.name.casefold()
                        suffix = Path(name).suffix
                        # Unknown suffixes can themselves contain secrets: no raw suffix output.
                        extension_counts[suffix if suffix in KNOWN_EXTENSIONS else "other_or_none"] += 1
                        category = next((kind for kind, suffixes in EXTENSIONS.items() if suffix in suffixes), "other")
                        category_counts[category] += 1
                        report["regular_files"] += 1
                        report["regular_file_bytes"] += info.st_size
                        report["files_over_100_mib"] += int(info.st_size > 100 * 1024 * 1024)
                        report["license_name_candidates"] += int(name in LICENSE_NAMES)
                        report["names_requiring_private_review"] += int(any(cue in name for cue in REVIEW_NAME_CUES))
                    except OSError:
                        report["errors"] += 1
        except OSError:
            report["errors"] += 1
    if report["status"] == "complete" and (report["errors"] or report["depth_limited_directories"]):
        report["status"] = "partial"
    report["extension_counts"] = dict(sorted(extension_counts.items()))
    report["category_counts"] = dict(sorted(category_counts.items()))
    report["excluded_directory_counts"] = dict(sorted(excluded_counts.items()))
    report["scope"] = "Metadata of ordinary files; dependency/git directories excluded; no file contents or names in output."
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", help="Local directories to summarize; their paths are not written to the report.")
    parser.add_argument("--max-files", type=int, default=200000)
    parser.add_argument("--max-entries", type=int, default=500000)
    parser.add_argument("--max-depth", type=int, default=32)
    args = parser.parse_args(argv)
    if len(args.directories) > 20:
        parser.error("At most 20 roots are accepted per invocation.")
    try:
        reports = [{"root_id": index, **inventory(path, max_files=args.max_files, max_entries=args.max_entries, max_depth=args.max_depth)}
                   for index, path in enumerate(args.directories, 1)]
    except ValueError:
        parser.error("Use max-files 1..200000, max-entries 1..500000 and max-depth 0..64.")
    print(json.dumps({"schema_version": 1, "roots": reports}, indent=2))
    return 0 if all(item["status"] == "complete" for item in reports) else 2


if __name__ == "__main__":
    raise SystemExit(main())
