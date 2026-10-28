#!/usr/bin/env python3
"""Compare aggregate response observations from an offline synthetic/auth test CSV."""

import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import stat
from statistics import median


FIELDS = {"cohort", "status_code", "response_bytes", "latency_ms"}
MAX_BYTES = 8 * 1024 * 1024
MAX_ROWS = 100000


def read_observations(path):
    """Strict schema excludes usernames, emails, tokens and raw response bodies."""
    path = Path(path)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Input must be a regular CSV file.")
    if info.st_size > MAX_BYTES:
        raise ValueError("Input exceeds the 8 MiB limit.")
    groups = {"known": [], "unknown": []}
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(reader.fieldnames) != len(FIELDS) or set(reader.fieldnames) != FIELDS:
            raise ValueError("CSV must contain exactly the four documented columns.")
        for row_number, row in enumerate(reader, 2):
            if row_number > MAX_ROWS + 1:
                raise ValueError("Input exceeds the 100000-row limit.")
            try:
                if set(row) != FIELDS or row["cohort"] not in groups:
                    raise ValueError
                code = int(row["status_code"])
                size = int(row["response_bytes"])
                latency = float(row["latency_ms"])
                if not (100 <= code <= 599 and 0 <= size <= 100 * 1024 * 1024 and math.isfinite(latency) and 0 <= latency <= 3600000):
                    raise ValueError
            except (ValueError, TypeError):
                # Never echo a rejected value, which might contain personal information.
                raise ValueError(f"Invalid observation on CSV line {row_number}.") from None
            groups[row["cohort"]].append((code, size, latency))
    return groups


def analyze(groups, min_samples=20):
    if not 1 <= min_samples <= MAX_ROWS // 2:
        raise ValueError("Minimum sample count is outside the supported range.")
    summary = {}
    for name in ("known", "unknown"):
        rows = groups[name]
        summary[name] = {
            "samples": len(rows),
            "status_counts": dict(sorted(Counter(row[0] for row in rows).items())),
            "median_response_bytes": median(row[1] for row in rows) if rows else None,
            "median_latency_ms": round(median(row[2] for row in rows), 4) if rows else None,
        }
    a, b = summary["known"], summary["unknown"]
    result = {"schema_version": 1, "cohorts": summary, "minimum_samples_per_cohort": min_samples,
              "sample_status": "sufficient_for_summary" if min(a["samples"], b["samples"]) >= min_samples else "insufficient",
              "comparison": None,
              "interpretation": "Descriptive observations only; neither proof of account enumeration nor assurance of its absence."}
    if a["samples"] and b["samples"]:
        codes = set(a["status_counts"]) | set(b["status_counts"])
        distance = 0.5 * sum(abs(a["status_counts"].get(code, 0) / a["samples"] - b["status_counts"].get(code, 0) / b["samples"]) for code in codes)
        result["comparison"] = {
            "status_distribution_distance": round(distance, 6),
            "absolute_median_size_gap_bytes": abs(a["median_response_bytes"] - b["median_response_bytes"]),
            "absolute_median_latency_gap_ms": round(abs(a["median_latency_ms"] - b["median_latency_ms"]), 4),
        }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", help="CSV containing only the four documented non-identifying columns.")
    parser.add_argument("--min-samples", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        result = analyze(read_observations(args.csv_file), args.min_samples)
    except OSError:
        parser.error("Cannot read the input file.")
    except (UnicodeError, csv.Error):
        parser.error("Input must be a valid UTF-8 CSV.")
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
