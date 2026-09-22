from __future__ import annotations

import argparse
import os
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

from common import parse_time, read_csv, write_json, write_text


def summarize_storage_events(rows: list[dict[str, str]]) -> dict:
    by_date: Counter[str] = Counter()
    by_second: Counter[str] = Counter()
    ids: Counter[str] = Counter()

    for row in rows:
        dt = parse_time(row["TimeCreated"])
        by_date[dt.date().isoformat()] += 1
        by_second[dt.isoformat(sep=" ")] += 1
        ids[row.get("Id", "")] += 1

    largest_bursts = [
        {"timestamp": ts, "retry_events": count}
        for ts, count in by_second.most_common(10)
    ]

    return {
        "total_events": len(rows),
        "event_ids": dict(ids),
        "events_by_date": dict(sorted(by_date.items())),
        "largest_bursts": largest_bursts,
    }


def safe_io_benchmark(size_mb: int = 64, runs: int = 3) -> dict:
    if size_mb < 1 or size_mb > 512:
        raise ValueError("size_mb must be between 1 and 512.")
    if runs < 1 or runs > 10:
        raise ValueError("runs must be between 1 and 10.")

    block = b"0" * (1024 * 1024)
    results = []

    for run_no in range(1, runs + 1):
        fd, name = tempfile.mkstemp(prefix="week3_io_", suffix=".tmp")
        os.close(fd)
        path = Path(name)

        try:
            start = time.perf_counter()
            with path.open("wb", buffering=0) as handle:
                for _ in range(size_mb):
                    handle.write(block)
                handle.flush()
                os.fsync(handle.fileno())
            write_seconds = time.perf_counter() - start

            start = time.perf_counter()
            total_read = 0
            with path.open("rb", buffering=0) as handle:
                while chunk := handle.read(1024 * 1024):
                    total_read += len(chunk)
            read_seconds = time.perf_counter() - start

            results.append(
                {
                    "run": run_no,
                    "size_mb": size_mb,
                    "write_seconds": round(write_seconds, 4),
                    "write_mb_per_sec": round(size_mb / write_seconds, 2),
                    "read_seconds": round(read_seconds, 4),
                    "read_mb_per_sec": round(
                        (total_read / 1024 / 1024) / read_seconds, 2
                    ),
                }
            )
        finally:
            path.unlink(missing_ok=True)

    return {
        "runs": results,
        "average_write_mb_per_sec": round(
            sum(r["write_mb_per_sec"] for r in results) / len(results), 2
        ),
        "average_read_mb_per_sec": round(
            sum(r["read_mb_per_sec"] for r in results) / len(results), 2
        ),
        "note": (
            "This is a small controlled current-performance baseline. It does not "
            "reproduce or prove the historical cause of Event ID 153 retries."
        ),
    }


def run(
    evidence_dir: Path,
    output_dir: Path,
    benchmark_size_mb: int,
    benchmark_runs: int,
    skip_benchmark: bool,
) -> dict:
    storage_events = read_csv(evidence_dir / "storage_events_30days.csv")
    disks = read_csv(evidence_dir / "storage_devices.csv")
    reliability = read_csv(evidence_dir / "storage_reliability.csv")

    historical = summarize_storage_events(storage_events)
    benchmark = None
    if not skip_benchmark:
        benchmark = safe_io_benchmark(benchmark_size_mb, benchmark_runs)

    result = {
        "historical_evidence": historical,
        "disk_inventory": disks,
        "reliability_snapshot": reliability,
        "current_io_benchmark": benchmark,
        "interpretation": (
            "The laptop recorded repeated storage retry events despite Windows reporting "
            "the NVMe drive as healthy/online. That establishes a reliability incident, "
            "but does not prove physical disk failure. The controlled benchmark provides "
            "a current baseline only."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "wednesday_storage_investigation.json", result)

    lines = [
        "# Wednesday — Storage Reliability & I/O Performance Investigation",
        "",
        f"- Historical storage events analysed: **{historical['total_events']}**",
        f"- Event IDs: `{historical['event_ids']}`",
        "",
        "## Retry events by date",
        "",
    ]
    for date, count in historical["events_by_date"].items():
        lines.append(f"- {date}: **{count}**")

    lines += ["", "## Largest same-second bursts", ""]
    for burst in historical["largest_bursts"]:
        lines.append(
            f"- {burst['timestamp']}: **{burst['retry_events']}** retry events"
        )

    if disks:
        disk = disks[0]
        lines += [
            "",
            "## Disk inventory evidence",
            f"- Device: **{disk.get('FriendlyName', 'Unknown')}**",
            f"- Bus type: **{disk.get('BusType', 'Unknown')}**",
            f"- Health: **{disk.get('HealthStatus', 'Unknown')}**",
            f"- Operational status: **{disk.get('OperationalStatus', 'Unknown')}**",
            f"- Size: **{disk.get('SizeGB', 'Unknown')} GB**",
        ]

    if benchmark:
        lines += [
            "",
            "## Current controlled I/O baseline",
            "",
            f"- Test file size: **{benchmark_size_mb} MB**",
            f"- Runs: **{benchmark_runs}**",
            f"- Average sequential write: **{benchmark['average_write_mb_per_sec']} MB/s**",
            f"- Average sequential read: **{benchmark['average_read_mb_per_sec']} MB/s**",
            "",
            benchmark["note"],
        ]

    lines += [
        "",
        "## Interpretation",
        "",
        result["interpretation"],
        "",
        "### Safety",
        "",
        "The benchmark writes only a small temporary file, reads it, flushes the write, "
        "and deletes the temporary file. It does not modify Windows configuration or "
        "perform repair operations.",
    ]
    write_text(output_dir / "wednesday_storage_investigation.md", "\n".join(lines))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "reports")
    parser.add_argument("--size-mb", type=int, default=64)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--skip-benchmark", action="store_true")
    args = parser.parse_args()

    result = run(
        args.evidence_dir,
        args.output_dir,
        args.size_mb,
        args.runs,
        args.skip_benchmark,
    )

    historical = result["historical_evidence"]
    print("\nWEDNESDAY STORAGE INVESTIGATION")
    print("=" * 52)
    print(f"Historical retry events: {historical['total_events']}")
    if result["current_io_benchmark"]:
        bench = result["current_io_benchmark"]
        print(f"Avg write: {bench['average_write_mb_per_sec']} MB/s")
        print(f"Avg read:  {bench['average_read_mb_per_sec']} MB/s")
    print("Report saved in:", args.output_dir)


if __name__ == "__main__":
    main()
