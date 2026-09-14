"""
File Checker Utility
Demonstrates exceptions, modules and basic testing.
Checks whether a file exists and displays simple information about it.
"""

import os

def get_file_info(file_path):
    if not file_path:
        raise ValueError("File path cannot be empty.")

    if not os.path.exists(file_path):
        raise FileNotFoundError("The file does not exist.")

    if not os.path.isfile(file_path):
        raise ValueError("The path is not a file.")

    return {
        "name": os.path.basename(file_path),
        "size_bytes": os.path.getsize(file_path),
        "extension": os.path.splitext(file_path)[1] or "No extension"
    }

def run_basic_tests():
    print("\nRunning basic tests...")

    try:
        get_file_info("")
    except ValueError:
        print("Test 1 passed: Empty path handled correctly.")

    try:
        get_file_info("file_that_does_not_exist_12345.txt")
    except FileNotFoundError:
        print("Test 2 passed: Missing file handled correctly.")

def main():
    run_basic_tests()

    print("\n=== FILE CHECKER ===")
    file_path = input("Enter a file path: ").strip()

    try:
        information = get_file_info(file_path)

        print("\nFile found.")
        for key, value in information.items():
            print(f"{key}: {value}")

    except FileNotFoundError as error:
        print(f"Error: {error}")

    except ValueError as error:
        print(f"Error: {error}")

    except PermissionError:
        print("Error: You do not have permission to access this file.")

    except Exception as error:
        print(f"Unexpected error: {error}")

if __name__ == "__main__":
    main()
