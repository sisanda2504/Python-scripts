# Monday — Wi-Fi Root-Cause Investigation

- ASUS SmartConnect crashes analysed: **5**
- WLAN warning/error events analysed: **14**
- Crashes with a WLAN event within 2s: **5/5**
- Correlation rate: **100.0%**

## Repeated crash signature
- Version: `1.0.4.0`
- Exception: `0xc0000005`
- Fault offset: `0x00000000000069c9`

## Wireless driver evidence
- Device: **MediaTek Wi-Fi 6E MT7902 Wireless LAN Card**
- Provider: **MediaTek, Inc.**
- Driver version: **3.4.2.1304**
- Driver date: **2025/06/30 02:00:00**

## Correlated incidents

- 2026-09-16 19:36:02 — correlated: **YES** (0s difference)
- 2026-09-10 14:51:26 — correlated: **YES** (1s difference)
- 2026-08-30 15:02:02 — correlated: **YES** (1s difference)
- 2026-08-26 19:17:08 — correlated: **YES** (1s difference)
- 2026-08-26 19:16:02 — correlated: **YES** (1s difference)

## Interpretation

Repeated near-simultaneous ASUS SmartConnect crashes and WLAN module stops form a reproducible incident pattern. This supports a strong relationship hypothesis but does not, by itself, prove causation.

### Root-cause status

**Not yet proven.** The evidence is strong enough to justify a driver/utility interaction hypothesis, but a controlled verification step is still required.