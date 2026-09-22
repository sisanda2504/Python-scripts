# Thursday — Startup Configuration Drift Audit

- Startup entries analysed: **8**
- Desired-state status: **NON_COMPLIANT**
- Non-compliant findings: **1**

## Findings

### Microsoft Teams startup — **NON_COMPLIANT**
- Found: **2**, allowed: **1**
- Entry: `com.squirrel.Teams.Teams`
- Entry: `Teams`
- Recommendation: Review the legacy Squirrel Teams startup entry and the newer packaged Teams entry. Keep only the entry that matches the installed Teams version.

## Configuration-management principle

The JSON file defines the desired state. The audit compares the laptop's actual startup state with that desired state and reports drift. Remediation is generated as a reviewable plan instead of silently changing the Registry.