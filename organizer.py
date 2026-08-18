import json
from pathlib import Path
from datetime import datetime
import logging
import fnmatch
import shutil

logging.basicConfig(
    filename="organizer.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)

def load_config(config_path=None):
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_category(file_path, categories):
    extension = Path(file_path).suffix.lower()

    for category, extensions in categories.items():
        if extension in extensions:
            return category

    return "Others"

def scan_folder(folder_path, exclude_patterns=None):
    folder = Path(folder_path)
    exclude_patterns = exclude_patterns or []

    files = []
    for item in folder.iterdir():
        if not item.is_file():
            continue
        if any(fnmatch.fnmatch(item.name, pattern) for pattern in exclude_patterns):
            continue
        files.append(item)

    return files

def resolve_conflict(destination, reserved=None):
    reserved = reserved or set()

    if not destination.exists() and destination not in reserved:
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent

    counter = 1
    new_destination = parent / f"{stem}_{counter}{suffix}"
    while new_destination.exists() or new_destination in reserved:
        counter += 1
        new_destination = parent / f"{stem}_{counter}{suffix}"

    return new_destination

def build_plan(folder_path, config):
    folder = Path(folder_path)
    files = scan_folder(folder_path, config.get("exclude", []))

    plan = []
    reserved = set()
    for file in files:
        category = get_category(file, config["categories"])
        raw_destination = folder / category / file.name
        final_destination = resolve_conflict(raw_destination, reserved)
        reserved.add(final_destination)
        plan.append((file, final_destination))

    return plan

def print_plan(plan):
    if not plan:
        print("Файлов для организации не найдено.")
        return

    print("Будут перемещены:")
    for source, destination in plan:
        if destination.name == source.name:
            print(f"  {source.name} → {destination.parent.name}/")
        else:
            print(f"  {source.name} → {destination.parent.name}/{destination.name}")

def organize(folder_path, config):
    plan = build_plan(folder_path, config)
    results = []

    for source, final_destination in plan:
        final_destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(final_destination))
        logging.info(f"{source.name} → {final_destination.parent.name}/")
        results.append((source, final_destination))

    return results

def save_log(results, folder_path, log_path="organizer_log.json"):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "folder": str(folder_path),
        "moves": [
            {"from": str(source), "to": str(destination)}
            for source, destination in results
        ]
    }

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)

def undo(log_path="organizer_log.json"):
    if not Path(log_path).exists():
        print("Файл журнала не найден. Нечего отменять.")
        return

    with open(log_path, "r", encoding="utf-8") as f:
        log_entry = json.load(f)

    moves = log_entry["moves"]

    if not moves:
        print("В последней организации не было перемещений.")
        return

    restored = 0
    skipped = 0

    for move in reversed(moves):
        source = Path(move["to"])
        destination = Path(move["from"])

        if source.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            print(f"  {source.name} возвращён обратно")
            restored += 1
        else:
            print(f"  {source.name} не найден, пропускаем")
            skipped += 1

    print(f"↩️ Undo завершён. Возвращено файлов: {restored}, пропущено: {skipped}")