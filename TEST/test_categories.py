from organizer import get_category


CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png"],
    "Documents": [".pdf", ".docx", ".txt"],
}


def test_jpg_is_images():
    assert get_category("photo.jpg", CATEGORIES) == "Images"


def test_pdf_is_documents():
    assert get_category("report.pdf", CATEGORIES) == "Documents"


def test_unknown_extension_is_others():
    assert get_category("weird_file.xyz", CATEGORIES) == "Others"


def test_extension_is_case_insensitive():
    assert get_category("photo.JPG", CATEGORIES) == "Images"