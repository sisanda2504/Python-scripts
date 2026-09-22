from __future__ import annotations

import csv
import io
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


BASE_DIR = Path("Week_3_Targeted_Investigation")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = BASE_DIR / f"investigation_{STAMP}"


def run_ps(command: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout, result.stderr


def save_ps(name: str, command: str) -> tuple[int, str]:
    code, stdout, stderr = run_ps(command)
    path = OUT_DIR / name
    content = stdout if stdout.strip() else (
        "No rows returned.\n\n"
        f"Exit code: {code}\n"
        f"PowerShell stderr:\n{stderr.strip()}\n"
    )
    path.write_text(content, encoding="utf-8")
    return code, content


def csv_rows(content: str) -> list[dict[str, str]]:
    if not content.strip() or content.startswith("No rows returned."):
        return []
    try:
        return list(csv.DictReader(io.StringIO(content)))
    except Exception:
        return []


def find_error_codes(message: str) -> list[str]:
    return re.findall(r"0x[0-9A-Fa-f]{8}", message or "")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    note = """READ BEFORE SHARING

This investigation is read-only. It does not repair disks, uninstall drivers,
change Wi-Fi settings, modify startup programs, or install updates.

It intentionally avoids collecting:
- Wi-Fi SSIDs and passwords
- saved passwords
- browser history/cookies
- personal document contents
- Security event logs

Event messages may still contain local application paths or computer-specific
details. Review the generated files before sharing.
"""
    (OUT_DIR / "READ_BEFORE_SHARING.txt").write_text(note, encoding="utf-8")

    # 1. Storage investigation
    _, disks = save_ps(
        "storage_devices.csv",
        "Get-Disk | "
        "Select-Object Number,FriendlyName,SerialNumber,BusType,"
        "HealthStatus,OperationalStatus,PartitionStyle,"
        "@{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,2)}} | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    _, reliability = save_ps(
        "storage_reliability.csv",
        "Get-PhysicalDisk -ErrorAction SilentlyContinue | ForEach-Object { "
        "$pd=$_; "
        "try { "
        "$r=$pd | Get-StorageReliabilityCounter -ErrorAction Stop; "
        "[PSCustomObject]@{"
        "FriendlyName=$pd.FriendlyName;"
        "HealthStatus=$pd.HealthStatus;"
        "OperationalStatus=($pd.OperationalStatus -join ';');"
        "Temperature=$r.Temperature;"
        "TemperatureMax=$r.TemperatureMax;"
        "Wear=$r.Wear;"
        "PowerOnHours=$r.PowerOnHours;"
        "ReadErrorsTotal=$r.ReadErrorsTotal;"
        "ReadErrorsUncorrected=$r.ReadErrorsUncorrected;"
        "WriteErrorsTotal=$r.WriteErrorsTotal;"
        "WriteErrorsUncorrected=$r.WriteErrorsUncorrected"
        "} "
        "} catch { "
        "[PSCustomObject]@{"
        "FriendlyName=$pd.FriendlyName;"
        "HealthStatus=$pd.HealthStatus;"
        "OperationalStatus=($pd.OperationalStatus -join ';');"
        "Temperature='Unavailable';"
        "TemperatureMax='Unavailable';"
        "Wear='Unavailable';"
        "PowerOnHours='Unavailable';"
        "ReadErrorsTotal='Unavailable';"
        "ReadErrorsUncorrected='Unavailable';"
        "WriteErrorsTotal='Unavailable';"
        "WriteErrorsUncorrected='Unavailable'"
        "} "
        "} "
        "} | ConvertTo-Csv -NoTypeInformation"
    )

    _, storage_events = save_ps(
        "storage_events_30days.csv",
        "$start=(Get-Date).AddDays(-30); "
        "Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=$start} "
        "-ErrorAction SilentlyContinue | "
        "Where-Object {"
        "$_.ProviderName -in @('disk','storahci','stornvme','Ntfs','volmgr') "
        "-and $_.Id -in @(7,11,51,55,98,129,153,154,157,161)"
        "} | "
        "Select-Object TimeCreated,ProviderName,Id,LevelDisplayName,Message | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    # 2. Wi-Fi / driver investigation
    _, wifi_driver = save_ps(
        "wifi_driver_details.csv",
        "Get-CimInstance Win32_PnPSignedDriver -ErrorAction SilentlyContinue | "
        "Where-Object {"
        "$_.DeviceClass -eq 'NET' -and "
        "($_.DeviceName -match 'Wi-Fi|Wireless|MediaTek|802\\.11')"
        "} | "
        "Select-Object DeviceName,Manufacturer,DriverProviderName,"
        "DriverVersion,DriverDate,InfName,IsSigned | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    _, wifi_events = save_ps(
        "wifi_events_30days.csv",
        "$start=(Get-Date).AddDays(-30); "
        "Get-WinEvent -FilterHashtable @{"
        "LogName='System';"
        "ProviderName='Microsoft-Windows-WLAN-AutoConfig';"
        "StartTime=$start"
        "} -ErrorAction SilentlyContinue | "
        "Where-Object {$_.Level -in @(1,2,3)} | "
        "Select-Object TimeCreated,Id,LevelDisplayName,Message | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    _, asus_crashes = save_ps(
        "asus_wifi_utility_crashes_30days.csv",
        "$start=(Get-Date).AddDays(-30); "
        "Get-WinEvent -FilterHashtable @{"
        "LogName='Application';"
        "ProviderName='Application Error';"
        "Id=1000;"
        "StartTime=$start"
        "} -ErrorAction SilentlyContinue | "
        "Where-Object {$_.Message -match 'AsusWiFiSmartConnect'} | "
        "Select-Object TimeCreated,Id,LevelDisplayName,Message | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    # 3. Windows app update failures
    _, updates = save_ps(
        "app_update_failures_30days.csv",
        "$start=(Get-Date).AddDays(-30); "
        "Get-WinEvent -FilterHashtable @{"
        "LogName='System';"
        "ProviderName='Microsoft-Windows-WindowsUpdateClient';"
        "Id=20;"
        "StartTime=$start"
        "} -ErrorAction SilentlyContinue | "
        "Select-Object TimeCreated,Id,LevelDisplayName,Message | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    # 4. DNS and time-sync problems
    _, dns_time = save_ps(
        "dns_time_events_30days.csv",
        "$start=(Get-Date).AddDays(-30); "
        "Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=$start} "
        "-ErrorAction SilentlyContinue | "
        "Where-Object {"
        "($_.ProviderName -eq 'Microsoft-Windows-DNS-Client' -and $_.Id -eq 1014) "
        "-or "
        "($_.ProviderName -eq 'Microsoft-Windows-Time-Service' -and $_.Id -eq 134)"
        "} | "
        "Select-Object TimeCreated,ProviderName,Id,LevelDisplayName,Message | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    # 5. Startup configuration evidence
    _, startup = save_ps(
        "startup_items.csv",
        "Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue | "
        "Select-Object Name,Location,User,Command | "
        "ConvertTo-Csv -NoTypeInformation"
    )

    # Build a compact summary from the actual results.
    storage_rows = csv_rows(storage_events)
    wifi_rows = csv_rows(wifi_events)
    crash_rows = csv_rows(asus_crashes)
    update_rows = csv_rows(updates)
    dns_rows = csv_rows(dns_time)
    startup_rows = csv_rows(startup)
    reliability_rows = csv_rows(reliability)
    disk_rows = csv_rows(disks)

    storage_ids = Counter(r.get("Id", "") for r in storage_rows)
    wifi_ids = Counter(r.get("Id", "") for r in wifi_rows)
    update_codes: Counter[str] = Counter()
    for row in update_rows:
        for code in find_error_codes(row.get("Message", "")):
            update_codes[code.upper()] += 1

    teams_startups = [
        r for r in startup_rows
        if "team" in (r.get("Name", "") + " " + r.get("Command", "")).lower()
    ]

    summary = [
        "# Targeted Windows Troubleshooting Evidence",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Storage",
        f"- Relevant storage events in last 30 days: {len(storage_rows)}",
        f"- Event IDs: {dict(storage_ids)}",
        f"- Disks detected: {len(disk_rows)}",
        f"- Reliability rows returned: {len(reliability_rows)}",
        "",
        "## Wi-Fi / network driver",
        f"- WLAN warning/error events in last 30 days: {len(wifi_rows)}",
        f"- WLAN event IDs: {dict(wifi_ids)}",
        f"- ASUS WiFi Smart Connect crashes: {len(crash_rows)}",
        "",
        "## Windows app updates",
        f"- Installation-failure events in last 30 days: {len(update_rows)}",
        f"- Error codes found: {dict(update_codes)}",
        "",
        "## DNS / time synchronization",
        f"- DNS/time warning events in last 30 days: {len(dns_rows)}",
        "",
        "## Startup configuration",
        f"- Startup items detected: {len(startup_rows)}",
        f"- Teams-related startup entries: {len(teams_startups)}",
        "",
        "## Files generated",
        "- storage_devices.csv",
        "- storage_reliability.csv",
        "- storage_events_30days.csv",
        "- wifi_driver_details.csv",
        "- wifi_events_30days.csv",
        "- asus_wifi_utility_crashes_30days.csv",
        "- app_update_failures_30days.csv",
        "- dns_time_events_30days.csv",
        "- startup_items.csv",
        "",
        "This script collected evidence only. No repairs or configuration changes were made.",
    ]

    (OUT_DIR / "INVESTIGATION_SUMMARY.md").write_text(
        "\n".join(summary), encoding="utf-8"
    )

    zip_path = shutil.make_archive(str(OUT_DIR), "zip", root_dir=OUT_DIR)

    print("\nTargeted investigation complete.")
    print(f"Folder: {OUT_DIR.resolve()}")
    print(f"ZIP:    {Path(zip_path).resolve()}")
    print("\nNo system settings were changed.")
    print("Review READ_BEFORE_SHARING.txt before uploading the ZIP.")


if __name__ == "__main__":
    main()
