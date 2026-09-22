from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import read_csv, write_json, write_text


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Desired-state config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return (value or "").strip().lower()


def audit_startup(rows: list[dict[str, str]], config: dict) -> dict:
    findings = []
    groups = config.get("exclusive_groups", [])

    for group in groups:
        matches = []
        for row in rows:
            haystack = normalize(row.get("Name", "") + " " + row.get("Command", ""))
            if any(normalize(pattern) in haystack for pattern in group["match_any"]):
                matches.append(row)

        max_entries = int(group.get("max_entries", 1))
        if len(matches) > max_entries:
            findings.append(
                {
                    "type": "DUPLICATE_STARTUP_GROUP",
                    "group": group["name"],
                    "status": "NON_COMPLIANT",
                    "found": len(matches),
                    "allowed": max_entries,
                    "entries": [
                        {
                            "name": item.get("Name", ""),
                            "command": item.get("Command", ""),
                            "location": item.get("Location", ""),
                        }
                        for item in matches
                    ],
                    "recommendation": group.get("recommendation", ""),
                }
            )
        else:
            findings.append(
                {
                    "type": "DUPLICATE_STARTUP_GROUP",
                    "group": group["name"],
                    "status": "COMPLIANT",
                    "found": len(matches),
                    "allowed": max_entries,
                    "entries": [
                        {"name": item.get("Name", ""), "command": item.get("Command", "")}
                        for item in matches
                    ],
                }
            )

    non_compliant = [f for f in findings if f["status"] != "COMPLIANT"]
    return {
        "startup_entries_analyzed": len(rows),
        "status": "NON_COMPLIANT" if non_compliant else "COMPLIANT",
        "non_compliant_findings": len(non_compliant),
        "findings": findings,
    }


def create_remediation_plan(result: dict) -> list[dict]:
    plan = []
    for finding in result["findings"]:
        if finding["status"] == "NON_COMPLIANT":
            plan.append(
                {
                    "group": finding["group"],
                    "action": "REVIEW_AND_DISABLE_REDUNDANT_ENTRY",
                    "reason": (
                        f"{finding['found']} startup entries detected; desired maximum "
                        f"is {finding['allowed']}."
                    ),
                    "important": (
                        "This project intentionally generates a plan only. It does not "
                        "edit the Windows Registry or disable startup apps automatically."
                    ),
                }
            )
    return plan


def run(evidence_dir: Path, config_path: Path, output_dir: Path) -> dict:
    rows = read_csv(evidence_dir / "startup_items.csv")
    config = load_config(config_path)
    result = audit_startup(rows, config)
    plan = create_remediation_plan(result)
    result["remediation_plan"] = plan

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "thursday_startup_config_audit.json", result)

    lines = [
        "# Thursday — Startup Configuration Drift Audit",
        "",
        f"- Startup entries analysed: **{result['startup_entries_analyzed']}**",
        f"- Desired-state status: **{result['status']}**",
        f"- Non-compliant findings: **{result['non_compliant_findings']}**",
        "",
        "## Findings",
        "",
    ]
    for finding in result["findings"]:
        lines.append(
            f"### {finding['group']} — **{finding['status']}**"
        )
        lines.append(
            f"- Found: **{finding['found']}**, allowed: **{finding['allowed']}**"
        )
        for entry in finding.get("entries", []):
            lines.append(f"- Entry: `{entry.get('name', '')}`")
        if finding.get("recommendation"):
            lines.append(f"- Recommendation: {finding['recommendation']}")
        lines.append("")

    lines += [
        "## Configuration-management principle",
        "",
        "The JSON file defines the desired state. The audit compares the laptop's "
        "actual startup state with that desired state and reports drift. Remediation "
        "is generated as a reviewable plan instead of silently changing the Registry.",
    ]

    write_text(output_dir / "thursday_startup_config_audit.md", "\n".join(lines))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent / "config" / "desired_startup_state.json",
    )
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "reports")
    args = parser.parse_args()

    result = run(args.evidence_dir, args.config, args.output_dir)
    print("\nTHURSDAY CONFIGURATION DRIFT AUDIT")
    print("=" * 52)
    print("Status:", result["status"])
    for finding in result["findings"]:
        print(
            f"{finding['group']}: {finding['status']} "
            f"({finding['found']}/{finding['allowed']})"
        )
    print("Report saved in:", args.output_dir)


if __name__ == "__main__":
    main()
