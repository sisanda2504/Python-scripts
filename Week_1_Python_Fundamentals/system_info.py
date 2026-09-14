"""
System Information Utility
Shows basic information about the computer.
"""

import platform
import os
import socket

def get_system_info():
    return {
        "Computer Name": socket.gethostname(),
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Processor": platform.processor() or "Not available",
        "Python Version": platform.python_version(),
        "Current User": os.getenv("USERNAME") or os.getenv("USER") or "Unknown"
    }

def main():
    print("\n=== SYSTEM INFORMATION ===")
    info = get_system_info()

    for key, value in info.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
