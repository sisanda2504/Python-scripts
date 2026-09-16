import unittest

from file_organizer_improved import get_category


class TestFileOrganizer(unittest.TestCase):

    def test_image_category(self):
        self.assertEqual(get_category(".jpg"), "Images")

    def test_document_category(self):
        self.assertEqual(get_category(".pdf"), "Documents")

    def test_spreadsheet_category(self):
        self.assertEqual(get_category(".csv"), "Spreadsheets")

    def test_python_category(self):
        self.assertEqual(get_category(".py"), "Python_Files")

    def test_unknown_category(self):
        self.assertEqual(get_category(".xyz"), "Other")


if __name__ == "__main__":
    unittest.main()