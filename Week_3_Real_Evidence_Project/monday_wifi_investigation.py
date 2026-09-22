from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import parse_time, read_csv, write_json, write_text


CRASH_FILE = "asus_wifi_utility_crashes_30days.csv"
WLAN_FILE = "wifi_events_30days.csv"
DRIVER_FILE = "wifi_driver_details.csv"


def extract_crash_details(message: str) -> dict[str, str]:
    patterns = {
        "application": r"Faulting application name:\s*([^,\r\n]+)",
        "version": r"Faulting application name:.*?version:\s*([^,\r\n]+)",
        "exception_code": r"Exception code:\s*(0x[0-9A-Fa-f]+)",
        "fault_offset": r"Fault offset:\s*(0x[0-9A-Fa-f]+)",
    }
    details = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, message, flags=re.DOTALL)
        details[key] = match.group(1).strip() if match else "Unknown"
    return details


def correlate_incidents(
    crashes: list[dict[str, str]],
    wlan_events: list[dict[str, str]],
    threshold_seconds: int = 2,
) -> list[dict]:
    wlan = []
    for row in wlan_events:
        wlan.append(
            {
                "time": parse_time(row["TimeCreated"]),
                "id": row.get("Id", ""),
                "message": row.get("Message", ""),
            }
        )

    correlations = []
    for crash in crashes:
        crash_time = parse_time(crash["TimeCreated"])
        details = extract_crash_details(crash.get("Message", ""))

        candidates = []
        for event in wlan:
            delta = abs((event["time"] - crash_time).total_seconds())
            if delta <= threshold_seconds:
                candidates.append((delta, event))

        candidates.sort(key=lambda item: item[0])
        nearest = candidates[0] if candidates else None

        correlations.append(
            {
                "crash_time": crash_time.isoformat(sep=" "),
                "application": details["application"],
                "version": details["version"],
                "exception_code": details["exception_code"],
                "fault_offset": details["fault_offset"],
                "correlated": bool(nearest),
                "wlan_time": nearest[1]["time"].isoformat(sep=" ") if nearest else None,
                "wlan_event_id": nearest[1]["id"] if nearest else None,
                "time_difference_seconds": nearest[0] if nearest else None,
            }
        )
    return correlations


def select_mediatek_driver(rows: list[dict[str, str]]) -> dict[str, str] | None:
    for row in rows:
        text = " ".join(str(v) for v in row.values()).lower()
        if "mediatek" in text and "wi-fi" in text:
            return row
    return None


def investigate(evidence_dir: Path, output_dir: Path, threshold: int = 2) -> dict:
    crashes = read_csv(evidence_dir / CRASH_FILE)
    wlan_events = read_csv(evidence_dir / WLAN_FILE)
    drivers = read_csv(evidence_dir / DRIVER_FILE)

    correlations = correlate_incidents(crashes, wlan_events, threshold)
    correlated_count = sum(1 for row in correlations if row["correlated"])
    crash_signatures = sorted(
        {
            (
                row["version"],
                row["exception_code"],
                row["fault_offset"],
            )
            for row in correlations
        }
    )
    driver = select_mediatek_driver(drivers)

    result = {
        "investigation": "ASUS WiFi SmartConnect / MediaTek WLAN event correlation",
        "crashes_analyzed": len(crashes),
        "wlan_events_analyzed": len(wlan_events),
        "correlation_window_seconds": threshold,
        "correlated_crashes": correlated_count,
        "correlation_rate_percent": round(
            (correlated_count / len(crashes) * 100) if crashes else 0, 1
        ),
        "unique_crash_signatures": [
            {
                "version": s[0],
                "exception_code": s[1],
                "fault_offset": s[2],
            }
            for s in crash_signatures
        ],
        "wifi_driver": driver,
        "correlations": correlations,
        "finding": (
            "Repeated near-simultaneous ASUS SmartConnect crashes and WLAN module "
            "stops form a reproducible incident pattern. This supports a strong "
            "relationship hypothesis but does not, by itself, prove causation."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "monday_wifi_investigation.json", result)

    lines = [
        "# Monday — Wi-Fi Root-Cause Investigation",
        "",
        f"- ASUS SmartConnect crashes analysed: **{len(crashes)}**",
        f"- WLAN warning/error events analysed: **{len(wlan_events)}**",
        f"- Crashes with a WLAN event within {threshold}s: **{correlated_count}/{len(crashes)}**",
        f"- Correlation rate: **{result['correlation_rate_percent']}%**",
        "",
        "## Repeated crash signature",
    ]
    for signature in result["unique_crash_signatures"]:
        lines += [
            f"- Version: `{signature['version']}`",
            f"- Exception: `{signature['exception_code']}`",
            f"- Fault offset: `{signature['fault_offset']}`",
        ]

    if driver:
        lines += [
            "",
            "## Wireless driver evidence",
            f"- Device: **{driver.get('DeviceName', 'Unknown')}**",
            f"- Provider: **{driver.get('DriverProviderName', 'Unknown')}**",
            f"- Driver version: **{driver.get('DriverVersion', 'Unknown')}**",
            f"- Driver date: **{driver.get('DriverDate', 'Unknown')}**",
        ]

    lines += ["", "## Correlated incidents", ""]
    for row in correlations:
        status = "YES" if row["correlated"] else "NO"
        lines.append(
            f"- {row['crash_time']} — correlated: **{status}**"
            + (
                f" ({row['time_difference_seconds']:.0f}s difference)"
                if row["correlated"]
                else ""
            )
        )

    lines += [
        "",
        "## Interpretation",
        "",
        result["finding"],
        "",
        "### Root-cause status",
        "",
        "**Not yet proven.** The evidence is strong enough to justify a driver/utility "
        "interaction hypothesis, but a controlled verification step is still required.",
    ]
    write_text(output_dir / "monday_wifi_investigation.md", "\n".join(lines))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "reports")
    parser.add_argument("--window", type=int, default=2)
    args = parser.parse_args()

    result = investigate(args.evidence_dir, args.output_dir, args.window)
    print("\nMONDAY WI-FI INVESTIGATION")
    print("=" * 52)
    print(f"Crashes analysed:       {result['crashes_analyzed']}")
    print(f"WLAN events analysed:   {result['wlan_events_analyzed']}")
    print(
        f"Correlated crashes:     {result['correlated_crashes']}/"
        f"{result['crashes_analyzed']}"
    )
    print(f"Correlation rate:       {result['correlation_rate_percent']}%")
    print("\nEvidence report saved in:", args.output_dir)


if __name__ == "__main__":
    main()
