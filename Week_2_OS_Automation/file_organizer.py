import os
import shutil


FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".txt", ".doc", ".docx"],
    "Spreadsheets": [".csv", ".xls", ".xlsx"],
    "Python_Files": [".py"],
    "Archives": [".zip", ".rar"],
}


def get_category(file_extension):
    """
    Determine the category of a file based on its extension.
    """

    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category

    return "Other"


def organize_files(folder_path):
    """
    Organise files inside a folder into category folders.
    """

    if not os.path.exists(folder_path):
        print("The folder does not exist.")
        return

    if not os.path.isdir(folder_path):
        print("The path provided is not a folder.")
        return

    files_moved = 0

    for file_name in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file_name)

        # Ignore directories
        if os.path.isdir(file_path):
            continue

        # Get file extension
        _, extension = os.path.splitext(file_name)

        category = get_category(extension)

        category_folder = os.path.join(folder_path, category)

        # Create category folder if it does not exist
        os.makedirs(category_folder, exist_ok=True)

        destination = os.path.join(category_folder, file_name)

        # Move the file
        shutil.move(file_path, destination)

        print(f"Moved: {file_name} -> {category}/")

        files_moved += 1

    print()
    print(f"Organisation complete. {files_moved} file(s) moved.")


def main():
    print("FILE ORGANIZER")
    print("----------------")

    folder_path = input("Enter the folder path you want to organise: ").strip()

    organize_files(folder_path)


if __name__ == "__main__":
    main()