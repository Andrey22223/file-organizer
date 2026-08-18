import json

from organizer import load_config, scan_folder


def test_load_config_reads_real_config_file():
    # Проверяем реальный config.json проекта, а не тестовую заглушку —
    # так тест поймает, если кто-то случайно сломает синтаксис файла
    config = load_config()

    assert "categories" in config
    assert "Images" in config["categories"]


def test_load_config_from_custom_path(tmp_path):
    custom_config = {"categories": {"Test": [".xyz"]}, "exclude": []}
    config_file = tmp_path / "custom.json"
    config_file.write_text(json.dumps(custom_config), encoding="utf-8")

    config = load_config(config_file)

    assert config["categories"]["Test"] == [".xyz"]


def test_scan_folder_excludes_ds_store(tmp_path):
    (tmp_path / "photo.jpg").touch()
    (tmp_path / ".DS_Store").touch()

    files = scan_folder(tmp_path, exclude_patterns=[".DS_Store"])
    names = [f.name for f in files]

    assert "photo.jpg" in names
    assert ".DS_Store" not in names


def test_scan_folder_excludes_wildcard_pattern(tmp_path):
    (tmp_path / "document.docx").touch()
    (tmp_path / "~$document.docx").touch()

    files = scan_folder(tmp_path, exclude_patterns=["~$*"])
    names = [f.name for f in files]

    assert "document.docx" in names
    assert "~$document.docx" not in names


def test_scan_folder_ignores_subfolders(tmp_path):
    (tmp_path / "file.txt").touch()
    (tmp_path / "subfolder").mkdir()

    files = scan_folder(tmp_path)
    names = [f.name for f in files]

    assert "file.txt" in names
    assert "subfolder" not in names
    