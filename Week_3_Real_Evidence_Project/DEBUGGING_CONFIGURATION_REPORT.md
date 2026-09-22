# Week 3 Debugging and Configuration-Management Report

## 1. Purpose

The purpose of this work was to investigate real reliability and configuration issues
from a Windows laptop using repeatable Python automation. The project does not depend on
invented failures. Windows Event Logs and configuration evidence were collected first,
then analyzed.

## 2. Monday — Troubleshooting and root-cause investigation

### Technical problem

Repeated Wi-Fi-related events were found. `AsusWiFiSmartConnect.exe` crashed five times,
while the MediaTek WLAN extensibility component also stopped repeatedly.

### Troubleshooting process

1. Collected Application and System event evidence.
2. Isolated ASUS SmartConnect application crashes.
3. Isolated WLAN AutoConfig warning/error events.
4. Parsed timestamps with Python.
5. Compared each crash against nearby WLAN module-stop events.
6. Extracted application version, exception code and fault offset.
7. Compared the repeated incident signature.

### Evidence before remediation

- ASUS SmartConnect crashes: **5**
- WLAN warning/error events: **14**
- WLAN module-stop events: **13**
- Wireless adapter: **MediaTek Wi-Fi 6E MT7902**
- Driver version: **3.4.2.1304**
- Repeated application exception: **0xc0000005**
- Repeated fault offset: **0x69c9**

The Python correlation report should be attached as the primary evidence.

### Root-cause conclusion

The evidence demonstrates a repeatable relationship between ASUS SmartConnect crashes
and WLAN module stops. The timing is strong enough to justify a driver/utility
interaction hypothesis, but timestamp correlation alone does not prove which component
causes the other. This distinction prevents an unsupported root-cause claim.

### Prevention / next controlled step

- Verify ASUS and MediaTek driver/utility versions from the laptop manufacturer.
- Compare incident frequency before and after an approved driver/utility update or
  controlled disabling of the optional SmartConnect feature.
- Re-run the same evidence collector after the observation period.

---

## 3. Tuesday — Debugging, logging, tests and exception handling

### Technical problem

Windows recorded **30 application-update failure events** in the 30-day evidence.

### Evidence

- `0x80073D02`: **27 events**
- `0x80240016`: **3 events**

The analyzer records failures in a log file, validates malformed messages, raises clear
exceptions when evidence files are missing, and has unit tests for known parser cases.

### Verification

Run:

```powershell
python -m unittest discover -s tests -v
```

Paste the final test result here after running:

```text
[ADD YOUR LOCAL TEST OUTPUT]
```

---

## 4. Wednesday — Performance and system reliability

### Technical problem

Windows recorded **493 Disk Event ID 153 retry warnings** within 30 days.

### Evidence

The NVMe disk was reported as `Healthy` and `Online`, yet storage I/O operations were
repeatedly retried. This creates a real reliability investigation: a healthy status does
not remove the need to investigate repeated latency/retry events.

### Method

1. Count historical retry events.
2. Group them by date and exact second.
3. Identify burst behaviour.
4. Compare the events with disk inventory/health evidence.
5. Run a small current sequential I/O benchmark as a baseline.
6. Do **not** treat a current benchmark as proof of a historical cause.

### Local benchmark evidence

After running Wednesday's script, paste:

```text
Average write MB/s:
Average read MB/s:
Largest retry burst:
```

### Root-cause status

Unresolved from the available evidence. Possible storage-driver, firmware, transient
load, power-management or hardware paths require controlled follow-up. The script does
not falsely label the SSD as failed.

---

## 5. Thursday — Configuration management

### Technical problem

The startup inventory contains two Teams-related startup mechanisms:

- legacy Squirrel Teams startup;
- newer packaged `ms-teams.exe` startup.

### Desired state

Only one startup mechanism should exist for the active Teams installation.

### Configuration-management approach

A JSON file defines the desired state. Python compares actual evidence with that desired
state and reports configuration drift.

The tool does not automatically modify the Registry. Instead it produces a remediation
plan for review.

### Idempotence concept

Once an approved configuration change leaves one valid Teams startup mechanism, running
the audit repeatedly should produce the same `COMPLIANT` result without additional
changes.

---

## 6. Friday — Cloud / VM readiness

The analysis code is separated from the Windows evidence collection. The analyzers use
the Python standard library, making them portable to a fresh Python environment.

A GitHub Actions workflow runs unit tests using:

- Windows
- Ubuntu
- Python 3.11
- Python 3.12

This provides external evidence that the analysis code can run outside the original
development laptop.

After pushing to GitHub, add a screenshot or result from the Actions page here.

---

## 7. Overall learning

The most important troubleshooting lesson was to separate:

- symptom from root cause;
- correlation from causation;
- historical evidence from current measurements;
- detection from remediation;
- actual state from desired configuration state.

The project uses evidence first, then automation to make the investigation repeatable.
