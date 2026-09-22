from __future__ import annotations

import csv
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path


BASE_DIR = Path("Week_3_Real_Evidence")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = BASE_DIR / f"evidence_{STAMP}"


def run_command(command: str) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout, result.stderr


def run_powershell(filename: str, powershell_command: str, summary: list[str]) -> None:
    command = (
        'powershell -NoProfile -ExecutionPolicy Bypass -Command '
        f'"{powershell_command}"'
    )
    code, stdout, stderr = run_command(command)
    path = OUT_DIR / filename

    if stdout.strip():
        path.write_text(stdout, encoding="utf-8")
    else:
        path.write_text(
            f"No rows returned.\n\nPowerShell stderr:\n{stderr.strip()}\n",
            encoding="utf-8",
        )

    status = "OK" if code == 0 else f"COMMAND EXIT CODE {code}"
    summary.append(f"{filename}: {status}")


def collect_system_snapshot(summary: list[str]) -> None:
    total, used, free = shutil.disk_usage(Path.home())

    text = f"""WINDOWS TROUBLESHOOTING SYSTEM SNAPSHOT
Generated: {datetime.now().isoformat(timespec="seconds")}

Computer name: {socket.gethostname()}
Operating system: {platform.system()} {platform.release()}
OS version: {platform.version()}
Architecture: {platform.machine()}
Processor: {platform.processor()}
Python: {sys.version.split()[0]}

Disk containing user profile:
Total GB: {total / (1024 ** 3):.2f}
Used GB:  {used / (1024 ** 3):.2f}
Free GB:  {free / (1024 ** 3):.2f}
Usage %:  {(used / total) * 100:.1f}
"""
    (OUT_DIR / "system_snapshot.txt").write_text(text, encoding="utf-8")
    summary.append("system_snapshot.txt: OK")


def collect_developer_tools(summary: list[str]) -> None:
    checks = [
        ("Python locations", "where.exe python"),
        ("Python launcher locations", "where.exe py"),
        ("Installed Python interpreters", "py -0p"),
        ("Python version", "python --version"),
        ("pip locations", "where.exe pip"),
        ("pip version", "pip --version"),
        ("Git locations", "where.exe git"),
        ("Git version", "git --version"),
        ("Node locations", "where.exe node"),
        ("Node version", "node --version"),
        ("npm version", "npm --version"),
        ("Java locations", "where.exe java"),
        ("Java version", "java -version"),
    ]

    output = []
    for label, command in checks:
        code, stdout, stderr = run_command(command)
        value = (stdout + stderr).strip() or "(not found / no output)"
        output.append(f"=== {label} ===\n{value}\n")

    (OUT_DIR / "developer_toolchain.txt").write_text(
        "\n".join(output), encoding="utf-8"
    )
    summary.append("developer_toolchain.txt: OK")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary: list[str] = []

    privacy_note = """PRIVACY NOTE

This collector intentionally does NOT collect:
- saved passwords
- browser history
- browser cookies
- Wi-Fi passwords
- the Windows Security event log
- environment variables
- contents of personal documents

Application/System event messages can still contain usernames, file paths,
application names, or other machine-specific details. Review the evidence
files before sharing them.
"""
    (OUT_DIR / "READ_BEFORE_SHARING.txt").write_text(
        privacy_note, encoding="utf-8"
    )

    collect_system_snapshot(summary)
    collect_developer_tools(summary)

    event_common = (
        "$start=(Get-Date).AddDays(-7); "
        "Get-WinEvent -FilterHashtable @{{LogName='{log}'; Level=1,2,3; StartTime=$start}} "
        "-ErrorAction SilentlyContinue | "
        "Select-Object TimeCreated,ProviderName,Id,LevelDisplayName,Message | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    run_powershell(
        "application_events_last7days.csv",
        event_common.format(log="Application"),
        summary,
    )

    run_powershell(
        "system_events_last7days.csv",
        event_common.format(log="System"),
        summary,
    )

    run_powershell(
        "automatic_services_not_running.csv",
        "Get-CimInstance Win32_Service | "
        "Where-Object {$_.StartMode -eq 'Auto' -and $_.State -ne 'Running'} | "
        "Select-Object Name,DisplayName,State,StartMode,ExitCode | "
        "ConvertTo-Csv -NoTypeInformation",
        summary,
    )

    run_powershell(
        "scheduled_tasks_nonzero_result.csv",
        "Get-ScheduledTask | ForEach-Object { "
        "$task=$_; "
        "try { "
        "$info=Get-ScheduledTaskInfo -TaskName $task.TaskName -TaskPath $task.TaskPath -ErrorAction Stop; "
        "[PSCustomObject]@{"
        "TaskPath=$task.TaskPath;"
        "TaskName=$task.TaskName;"
        "State=$task.State;"
        "LastRunTime=$info.LastRunTime;"
        "LastTaskResult=$info.LastTaskResult;"
        "NextRunTime=$info.NextRunTime"
        "} "
        "} catch {} "
        "} | Where-Object {$_.LastTaskResult -ne 0} | "
        "ConvertTo-Csv -NoTypeInformation",
        summary,
    )

    run_powershell(
        "top_memory_processes.csv",
        "Get-Process | Sort-Object WorkingSet64 -Descending | "
        "Select-Object -First 25 ProcessName,Id,"
        "@{Name='MemoryMB';Expression={[math]::Round($_.WorkingSet64/1MB,1)}},"
        "@{Name='CPUSeconds';Expression={if ($null -eq $_.CPU) {0} else {[math]::Round($_.CPU,1)}}} | "
        "ConvertTo-Csv -NoTypeInformation",
        summary,
    )

    run_powershell(
        "network_adapters.csv",
        "Get-NetAdapter -ErrorAction SilentlyContinue | "
        "Select-Object Name,InterfaceDescription,Status,LinkSpeed | "
        "ConvertTo-Csv -NoTypeInformation",
        summary,
    )

    run_powershell(
        "startup_items.csv",
        "Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue | "
        "Select-Object Name,Location,User,Command | "
        "ConvertTo-Csv -NoTypeInformation",
        summary,
    )

    summary_text = f"""WINDOWS TROUBLESHOOTING EVIDENCE COLLECTION
Generated: {datetime.now().isoformat(timespec="seconds")}

Evidence directory:
{OUT_DIR.resolve()}

Collection status:
""" + "\n".join(f"- {line}" for line in summary)

    (OUT_DIR / "SUMMARY.txt").write_text(summary_text, encoding="utf-8")

    zip_base = str(OUT_DIR)
    zip_path = shutil.make_archive(zip_base, "zip", root_dir=OUT_DIR)

    print("\nEvidence collection complete.")
    print(f"Folder: {OUT_DIR.resolve()}")
    print(f"ZIP:    {Path(zip_path).resolve()}")
    print("\nReview READ_BEFORE_SHARING.txt before uploading the ZIP.")


if __name__ == "__main__":
    main()
