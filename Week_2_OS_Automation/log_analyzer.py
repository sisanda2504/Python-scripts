import re


def analyze_log_file(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        error_lines = []
        dates = []
        ip_addresses = []

        date_pattern = r"\b\d{4}-\d{2}-\d{2}\b"
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

        for line in lines:
            if "ERROR" in line.upper():
                error_lines.append(line.strip())

            found_dates = re.findall(date_pattern, line)
            dates.extend(found_dates)

            found_ips = re.findall(ip_pattern, line)
            ip_addresses.extend(found_ips)

        print("\nLOG ANALYSIS RESULTS")
        print("--------------------")

        print(f"\nErrors found: {len(error_lines)}")
        for error in error_lines:
            print(error)

        print(f"\nDates found: {len(dates)}")
        for date in dates:
            print(date)

        print(f"\nIP addresses found: {len(ip_addresses)}")
        for ip in ip_addresses:
            print(ip)

    except FileNotFoundError:
        print("Error: The log file could not be found.")

    except PermissionError:
        print("Error: You do not have permission to read this file.")

    except Exception as error:
        print(f"Unexpected error: {error}")


def main():
    print("LOG FILE ANALYZER")
    print("-----------------")

    file_path = input("Enter the path of the log file: ").strip()

    analyze_log_file(file_path)


if __name__ == "__main__":
    main()