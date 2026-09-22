from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path

from common import write_json, write_text


def check_write_permission(path: Path) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    try:
        fd, test_path = tempfile.mkstemp(dir=path, prefix="write_test_", suffix=".tmp")
        os.close(fd)
        Path(test_path).unlink(missing_ok=True)
        return True
    except OSError:
        return False


def run_checks(project_root: Path, evidence_dir: Path | None) -> dict:
    required_project_files = [
        "monday_wifi_investigation.py",
        "tuesday_update_failure_analyzer.py",
        "wednesday_storage_investigation.py",
        "thursday_startup_config_audit.py",
        "common.py",
        "config/desired_startup_state.json",
        "tests/test_week3.py",
    ]

    checks = []

    def add(name: str, passed: bool, details: str):
        checks.append(
            {"check": name, "status": "PASS" if passed else "FAIL", "details": details}
        )

    add(
        "Python >= 3.10",
        sys.version_info >= (3, 10),
        f"Detected Python {platform.python_version()}",
    )
    add(
        "Project directory writable",
        check_write_permission(project_root / "reports"),
        str(project_root / "reports"),
    )
    add(
        "Git available",
        shutil.which("git") is not None,
        shutil.which("git") or "git not found on PATH",
    )

    for relative in required_project_files:
        target = project_root / relative
        add(f"Required file: {relative}", target.exists(), str(target))

    if platform.system() == "Windows":
        add(
            "PowerShell available",
            shutil.which("powershell") is not None or shutil.which("pwsh") is not None,
            shutil.which("powershell") or shutil.which("pwsh") or "Not found",
        )
    else:
        add(
            "Cross-platform parser mode",
            True,
            "Non-Windows environment can run CSV analyzers and unit tests; Windows-only evidence collection is skipped.",
        )

    if evidence_dir is not None:
        required_evidence = [
            "wifi_events_30days.csv",
            "asus_wifi_utility_crashes_30days.csv",
            "wifi_driver_details.csv",
            "app_update_failures_30days.csv",
            "storage_events_30days.csv",
            "storage_devices.csv",
            "storage_reliability.csv",
            "startup_items.csv",
        ]
        for name in required_evidence:
            add(
                f"Evidence file: {name}",
                (evidence_dir / name).exists(),
                str(evidence_dir / name),
            )

    failed = [c for c in checks if c["status"] == "FAIL"]
    return {
        "environment": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "architecture": platform.machine(),
        },
        "status": "READY" if not failed else "NOT_READY",
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "checks": checks,
        "deployment_note": (
            "The evidence analyzers use the Python standard library and are portable. "
            "Raw Windows evidence collection remains Windows-specific."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "reports")
    args = parser.parse_args()

    result = run_checks(args.project_root.resolve(), args.evidence_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "friday_deployment_readiness.json", result)

    lines = [
        "# Friday — VM / Cloud Deployment Readiness",
        "",
        f"Overall status: **{result['status']}**",
        f"- Passed: **{result['checks_passed']}**",
        f"- Failed: **{result['checks_failed']}**",
        "",
        "## Checks",
        "",
    ]
    for check in result["checks"]:
        lines.append(
            f"- **{check['status']}** — {check['check']} — {check['details']}"
        )

    lines += [
        "",
        "## Deployment interpretation",
        "",
        result["deployment_note"],
        "",
        "GitHub Actions in `.github/workflows/week3-tests.yml` runs the unit tests on "
        "both Windows and Ubuntu. That gives external evidence that the analysis code "
        "is not limited to one development machine.",
    ]
    write_text(args.output_dir / "friday_deployment_readiness.md", "\n".join(lines))

    print("\nFRIDAY DEPLOYMENT READINESS")
    print("=" * 52)
    print("Status:", result["status"])
    print(f"Passed: {result['checks_passed']}")
    print(f"Failed: {result['checks_failed']}")
    print("Report saved in:", args.output_dir)


if __name__ == "__main__":
    main()
