from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from monday_wifi_investigation import correlate_incidents, extract_crash_details
from tuesday_update_failure_analyzer import analyze_updates, parse_update_message
from thursday_startup_config_audit import audit_startup


class TestMondayWifiInvestigation(unittest.TestCase):
    def test_extract_crash_signature(self):
        message = """Faulting application name: AsusWiFiSmartConnect.exe, version: 1.0.4.0,
Exception code: 0xc0000005
Fault offset: 0x00000000000069c9"""
        result = extract_crash_details(message)
        self.assertEqual(result["application"], "AsusWiFiSmartConnect.exe")
        self.assertEqual(result["version"], "1.0.4.0")
        self.assertEqual(result["exception_code"], "0xc0000005")

    def test_correlates_nearby_events(self):
        crashes = [{
            "TimeCreated": "2026/09/16 19:36:02",
            "Message": "Faulting application name: AsusWiFiSmartConnect.exe, version: 1.0.4.0\nException code: 0xc0000005\nFault offset: 0x69c9"
        }]
        wlan = [{
            "TimeCreated": "2026/09/16 19:36:02",
            "Id": "10002",
            "Message": "WLAN Extensibility Module has stopped."
        }]
        result = correlate_incidents(crashes, wlan, 2)
        self.assertTrue(result[0]["correlated"])
        self.assertEqual(result[0]["time_difference_seconds"], 0)


class TestTuesdayUpdateAnalyzer(unittest.TestCase):
    def test_parse_packages_in_use(self):
        msg = (
            "Installation Failure: Windows failed to install the following update "
            "with error 0x80073D02: 9NKSQGP7F2NH-5319275A.WhatsAppDesktop."
        )
        result = parse_update_message(msg)
        self.assertEqual(result["error_code"], "0X80073D02")
        self.assertEqual(result["package"], "5319275A.WhatsAppDesktop")

    def test_empty_message_raises(self):
        with self.assertRaises(ValueError):
            parse_update_message("")

    def test_analyze_counts(self):
        rows = [
            {"Message": "Installation Failure: Windows failed to install the following update with error 0x80073D02: A-Test.App."},
            {"Message": "Installation Failure: Windows failed to install the following update with error 0x80240016: B-Runtime.App."},
        ]
        result = analyze_updates(rows)
        self.assertEqual(result["events_analyzed"], 2)
        self.assertEqual(result["error_counts"]["0X80073D02"], 1)


class TestThursdayConfigAudit(unittest.TestCase):
    def test_duplicate_teams_is_drift(self):
        rows = [
            {"Name": "com.squirrel.Teams.Teams", "Command": "Update.exe Teams.exe"},
            {"Name": "Teams", "Command": "ms-teams.exe"},
        ]
        config = {
            "exclusive_groups": [{
                "name": "Microsoft Teams startup",
                "match_any": ["com.squirrel.Teams.Teams", "ms-teams.exe"],
                "max_entries": 1,
            }]
        }
        result = audit_startup(rows, config)
        self.assertEqual(result["status"], "NON_COMPLIANT")
        self.assertEqual(result["findings"][0]["found"], 2)


if __name__ == "__main__":
    unittest.main()
