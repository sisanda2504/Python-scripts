import os
import platform
import shutil


def get_disk_usage():
    total, used, free = shutil.disk_usage("/")

    gb = 1024 ** 3

    print("\nDISK USAGE")
    print("--------------------")
    print(f"Total: {total / gb:.2f} GB")
    print(f"Used: {used / gb:.2f} GB")
    print(f"Free: {free / gb:.2f} GB")


def get_system_info():
    print("\nSYSTEM INFORMATION")
    print("--------------------")
    print(f"Operating System: {platform.system()}")
    print(f"OS Version: {platform.version()}")
    print(f"Computer Name: {platform.node()}")
    print(f"Processor: {platform.processor()}")
    print(f"CPU Count: {os.cpu_count()}")


def main():
    print("SYSTEM HEALTH CHECKER")
    print("=====================")

    get_system_info()
    get_disk_usage()


if __name__ == "__main__":
    main()