"""
Device Record Manager
Stores and manages simple IT device records using dictionaries and functions.
"""

devices = {
    "PC001": {
        "employee": "Sisanda",
        "device_type": "Laptop",
        "status": "Active"
    },
    "PC002": {
        "employee": "Thando",
        "device_type": "Desktop",
        "status": "Repair"
    }
}

def add_device(device_id, employee, device_type, status):
    if device_id in devices:
        print("A device with that ID already exists.")
        return

    devices[device_id] = {
        "employee": employee,
        "device_type": device_type,
        "status": status
    }

    print("Device added successfully.")

def view_devices():
    print("\n=== DEVICE RECORDS ===")

    if not devices:
        print("No device records found.")
        return

    for device_id, details in devices.items():
        print(f"\nDevice ID: {device_id}")
        print(f"Employee: {details['employee']}")
        print(f"Type: {details['device_type']}")
        print(f"Status: {details['status']}")

def main():
    while True:
        print("\n1. View devices")
        print("2. Add device")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            view_devices()

        elif choice == "2":
            device_id = input("Device ID: ").strip().upper()
            employee = input("Employee name: ").strip()
            device_type = input("Device type: ").strip()
            status = input("Device status: ").strip()

            if not device_id or not employee or not device_type or not status:
                print("All fields are required.")
            else:
                add_device(device_id, employee, device_type, status)

        elif choice == "3":
            print("Device Record Manager closed.")
            break

        else:
            print("Invalid option. Please choose 1, 2 or 3.")

if __name__ == "__main__":
    main()
