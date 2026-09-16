import os
import shutil
import logging


# Configure logging
logging.basicConfig(
    filename="file_organizer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".txt", ".doc", ".docx"],
    "Spreadsheets": [".csv", ".xls", ".xlsx"],
    "Python_Files": [".py"],
    "Archives": [".zip", ".rar"]
}


def get_category(file_extension):
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category

    return "Other"


def organize_files(folder_path):

    if not os.path.exists(folder_path):
        logging.error(f"Folder does not exist: {folder_path}")
        print("Error: The folder does not exist.")
        return

    if not os.path.isdir(folder_path):
        logging.error(f"Path is not a directory: {folder_path}")
        print("Error: The path provided is not a folder.")
        return

    files_moved = 0

    logging.info(f"Started organizing folder: {folder_path}")

    try:
        for file_name in os.listdir(folder_path):

            file_path = os.path.join(folder_path, file_name)

            if os.path.isdir(file_path):
                continue

            _, extension = os.path.splitext(file_name)

            category = get_category(extension)

            category_folder = os.path.join(folder_path, category)

            os.makedirs(category_folder, exist_ok=True)

            destination = os.path.join(category_folder, file_name)

            shutil.move(file_path, destination)

            logging.info(
                f"Moved {file_name} to {category}"
            )

            print(f"Moved: {file_name} -> {category}/")

            files_moved += 1

        logging.info(
            f"Organization completed. {files_moved} file(s) moved."
        )

        print(f"\nOrganization complete. {files_moved} file(s) moved.")

    except PermissionError:
        logging.exception("Permission denied while organizing files.")
        print("Error: Permission denied.")

    except Exception as error:
        logging.exception(f"Unexpected error: {error}")
        print(f"Unexpected error: {error}")


def main():
    print("IMPROVED FILE ORGANIZER")
    print("-----------------------")

    folder_path = input(
        "Enter the folder path you want to organize: "
    ).strip()

    organize_files(folder_path)


if __name__ == "__main__":
    main()