from organizer import organize, undo, save_log


TEST_CONFIG = {
    "categories": {
        "Images": [".jpg", ".png"],
        "Documents": [".pdf", ".txt"],
    },
    "exclude": [".DS_Store"],
}


def test_organize_moves_files_into_categories(tmp_path):
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "report.pdf").touch()

    results, errors = organize(tmp_path, TEST_CONFIG)

    assert len(results) == 2
    assert errors == []
    assert (tmp_path / "Images" / "photo.jpg").exists()
    assert (tmp_path / "Documents" / "report.pdf").exists()


def test_organize_on_empty_folder_returns_nothing(tmp_path):
    results, errors = organize(tmp_path, TEST_CONFIG)

    assert results == []
    assert errors == []


def test_organize_excludes_service_files(tmp_path):
    (tmp_path / "photo.jpg").touch()
    (tmp_path / ".DS_Store").touch()

    results, errors = organize(tmp_path, TEST_CONFIG)

    assert len(results) == 1
    assert (tmp_path / ".DS_Store").exists()  # остался на месте, не тронут


def test_undo_restores_files_to_original_location(tmp_path):
    (tmp_path / "photo.jpg").touch()

    results, errors = organize(tmp_path, TEST_CONFIG)
    log_path = tmp_path / "log.json"
    save_log(results, tmp_path, log_path=log_path)

    undo(log_path=log_path)

    assert (tmp_path / "photo.jpg").exists()
    assert not (tmp_path / "Images" / "photo.jpg").exists()


def test_undo_with_missing_log_file_does_not_crash(tmp_path, capsys):
    missing_log = tmp_path / "does_not_exist.json"

    undo(log_path=missing_log)

    captured = capsys.readouterr()
    assert "не найден" in captured.out.lower() or "не найдено" in captured.out.lower()


def test_undo_skips_manually_deleted_file(tmp_path):
    (tmp_path / "photo.jpg").touch()

    results, errors = organize(tmp_path, TEST_CONFIG)
    log_path = tmp_path / "log.json"
    save_log(results, tmp_path, log_path=log_path)

    # Пользователь вручную удалил файл после организации
    (tmp_path / "Images" / "photo.jpg").unlink()

    undo(log_path=log_path)

    assert not (tmp_path / "photo.jpg").exists()