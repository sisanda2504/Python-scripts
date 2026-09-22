# Week 3 — Real Windows Troubleshooting, Configuration Management and Cloud Readiness

This project uses **real diagnostic evidence collected from a Windows laptop** rather
than invented failures. Each day addresses a different Week 3 requirement.

## Monday — Troubleshooting methodology and root cause

`monday_wifi_investigation.py`

Correlates repeated `AsusWiFiSmartConnect.exe` application crashes with MediaTek WLAN
Extensibility Module stop events. It calculates timestamp differences and extracts the
repeated crash signature.

### Run

```powershell
python Week_3_Real_Evidence_Project\monday_wifi_investigation.py `
  --evidence-dir Week_3_Targeted_Investigation\investigation_20260921_111124
```

Evidence created:

- `reports/monday_wifi_investigation.md`
- `reports/monday_wifi_investigation.json`

The script deliberately distinguishes **correlation** from **proven causation**.

---

## Tuesday — Debugging, logging, testing and exception handling

`tuesday_update_failure_analyzer.py`

Analyzes real Windows application-update failures, validates event messages, classifies
error codes, writes structured logs, and handles missing/malformed evidence.

### Run

```powershell
python Week_3_Real_Evidence_Project\tuesday_update_failure_analyzer.py `
  --evidence-dir Week_3_Targeted_Investigation\investigation_20260921_111124
```

Run automated tests:

```powershell
cd Week_3_Real_Evidence_Project
python -m unittest discover -s tests -v
```

---

## Wednesday — Performance, resource usage and system reliability

`wednesday_storage_investigation.py`

Analyzes the historical Disk Event ID 153 retry pattern and performs a small,
controlled current I/O benchmark using a temporary file. The temporary file is deleted
after every run.

### Run

```powershell
python Week_3_Real_Evidence_Project\wednesday_storage_investigation.py `
  --evidence-dir Week_3_Targeted_Investigation\investigation_20260921_111124
```

To analyze history without generating benchmark I/O:

```powershell
python Week_3_Real_Evidence_Project\wednesday_storage_investigation.py `
  --evidence-dir Week_3_Targeted_Investigation\investigation_20260921_111124 `
  --skip-benchmark
```

The benchmark is a **current baseline** and is not presented as proof of the historical
Event 153 root cause.

---

## Thursday — Configuration management and infrastructure consistency

`thursday_startup_config_audit.py`

Compares the laptop's actual startup configuration with a JSON desired state. The
current evidence contains two Microsoft Teams startup mechanisms, so the audit detects
configuration drift.

### Run

```powershell
python Week_3_Real_Evidence_Project\thursday_startup_config_audit.py `
  --evidence-dir Week_3_Targeted_Investigation\investigation_20260921_111124 `
  --config Week_3_Real_Evidence_Project\config\desired_startup_state.json
```

The script creates a **remediation plan only**. It does not edit the Windows Registry or
disable startup applications automatically.

---

## Friday — Cloud / VM deployment readiness

`friday_environment_readiness.py`

Checks that the project has the runtime, files and permissions required to run in a
fresh environment. The project contains a GitHub Actions workflow that runs the unit
tests on **Windows and Ubuntu** using Python 3.11 and 3.12.

### Run

```powershell
python Week_3_Real_Evidence_Project\friday_environment_readiness.py `
  --evidence-dir Week_3_Targeted_Investigation\investigation_20260921_111124
```

After pushing the project to GitHub, open the **Actions** tab to capture evidence of the
cross-platform test results.

---

## Evidence already established from the laptop

The collected evidence showed:

- 5 ASUS WiFi SmartConnect crashes.
- 14 WLAN warning/error events, including 13 WLAN module-stop events.
- 30 Windows application-update failures.
- 493 Disk Event ID 153 retry warnings in 30 days.
- 8 startup entries, including 2 Teams-related startup mechanisms.

Raw Windows evidence should remain local because it can contain usernames, local paths,
device identifiers, and application details. Commit the **sanitized generated reports**
instead.

## Weekly deliverable

This folder includes:

- improved project code;
- automated tests;
- logging;
- exception handling;
- troubleshooting evidence;
- a desired-state configuration;
- a configuration-drift audit;
- a VM/cloud readiness checker;
- GitHub Actions CI;
- `DEBUGGING_CONFIGURATION_REPORT.md`.


## Run the full week in one command

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File Week_3_Real_Evidence_Project\run_all_week3.ps1 `
  -EvidenceDir "Week_3_Targeted_Investigation\investigation_20260921_111124"
```

This runs Monday through Friday and the unit-test suite. Wednesday performs the small
temporary-file I/O benchmark unless you run that script separately with
`--skip-benchmark`.

## Important Git privacy step

Do **not** commit the raw Windows evidence folders. They can contain local usernames,
paths and machine details. Before staging Week 3, you can locally exclude them without
changing the shared `.gitignore`:

```powershell
Add-Content .git\info\exclude "Week_3_Targeted_Investigation/"
Add-Content .git\info\exclude "Week_3_Real_Evidence/"
```

The generated Markdown/JSON reports in `Week_3_Real_Evidence_Project\reports` are the
better artefacts to commit as evidence.
