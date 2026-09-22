# Wednesday — Storage Reliability & I/O Performance Investigation

- Historical storage events analysed: **493**
- Event IDs: `{'153': 493}`

## Retry events by date

- 2026-08-23: **66**
- 2026-08-24: **80**
- 2026-08-27: **59**
- 2026-08-31: **79**
- 2026-09-08: **55**
- 2026-09-13: **77**
- 2026-09-14: **63**
- 2026-09-17: **14**

## Largest same-second bursts

- 2026-08-24 08:58:43: **80** retry events
- 2026-08-31 22:00:05: **79** retry events
- 2026-09-13 12:31:27: **77** retry events
- 2026-08-23 07:39:07: **66** retry events
- 2026-09-14 08:59:04: **63** retry events
- 2026-08-27 08:55:57: **59** retry events
- 2026-09-08 01:41:11: **55** retry events
- 2026-09-17 08:56:34: **14** retry events

## Disk inventory evidence
- Device: **NVMe HFS512GEJ9X108N**
- Bus type: **NVMe**
- Health: **Healthy**
- Operational status: **Online**
- Size: **476,94 GB**

## Current controlled I/O baseline

- Test file size: **64 MB**
- Runs: **3**
- Average sequential write: **1159.19 MB/s**
- Average sequential read: **2643.9 MB/s**

This is a small controlled current-performance baseline. It does not reproduce or prove the historical cause of Event ID 153 retries.

## Interpretation

The laptop recorded repeated storage retry events despite Windows reporting the NVMe drive as healthy/online. That establishes a reliability incident, but does not prove physical disk failure. The controlled benchmark provides a current baseline only.

### Safety

The benchmark writes only a small temporary file, reads it, flushes the write, and deletes the temporary file. It does not modify Windows configuration or perform repair operations.