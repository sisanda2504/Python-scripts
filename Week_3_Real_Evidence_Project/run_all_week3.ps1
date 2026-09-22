param(
    [Parameter(Mandatory=$true)]
    [string]$EvidenceDir
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n=== MONDAY: Wi-Fi investigation ===" -ForegroundColor Cyan
python "$ProjectDir\monday_wifi_investigation.py" --evidence-dir "$EvidenceDir"

Write-Host "`n=== TUESDAY: Update failure analysis ===" -ForegroundColor Cyan
python "$ProjectDir\tuesday_update_failure_analyzer.py" --evidence-dir "$EvidenceDir"

Write-Host "`n=== TUESDAY TESTS ===" -ForegroundColor Cyan
Push-Location $ProjectDir
python -m unittest discover -s tests -v
Pop-Location

Write-Host "`n=== WEDNESDAY: Storage investigation ===" -ForegroundColor Cyan
python "$ProjectDir\wednesday_storage_investigation.py" --evidence-dir "$EvidenceDir"

Write-Host "`n=== THURSDAY: Configuration drift audit ===" -ForegroundColor Cyan
python "$ProjectDir\thursday_startup_config_audit.py" --evidence-dir "$EvidenceDir"

Write-Host "`n=== FRIDAY: Deployment readiness ===" -ForegroundColor Cyan
python "$ProjectDir\friday_environment_readiness.py" --evidence-dir "$EvidenceDir"

Write-Host "`nWeek 3 run complete. Open:" -ForegroundColor Green
Write-Host "$ProjectDir\reports"
