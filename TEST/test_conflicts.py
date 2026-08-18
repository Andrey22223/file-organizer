from pathlib import Path

from organizer import resolve_conflict


def test_no_conflict_returns_same_path(tmp_path):
    destination = tmp_path / "photo.jpg"
    assert resolve_conflict(destination) == destination


def test_conflict_adds_counter(tmp_path):
    existing = tmp_path / "photo.jpg"
    existing.touch()

    destination = tmp_path / "photo.jpg"
    result = resolve_conflict(destination)

    assert result == tmp_path / "photo_1.jpg"


def test_multiple_conflicts_increment_counter(tmp_path):
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "photo_1.jpg").touch()

    destination = tmp_path / "photo.jpg"
    result = resolve_conflict(destination)

    assert result == tmp_path / "photo_2.jpg"


def test_reserved_paths_are_treated_as_taken(tmp_path):
    # Файл ещё не существует на диске, но уже "занят" в рамках текущего плана
    destination = tmp_path / "photo.jpg"
    reserved = {destination}

    result = resolve_conflict(destination, reserved)

    assert result == tmp_path / "photo_1.jpg"