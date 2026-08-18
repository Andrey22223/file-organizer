import argparse
from organizer import load_config, build_plan, print_plan, organize, save_log, undo
from pathlib import Path
import json

def validate_folder(folder_path):
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Ошибка: папка '{folder_path}' не найдена.")
        return False

    if not folder.is_dir():
        print(f"Ошибка: '{folder_path}' — это не папка.")
        return False

    return True

def main():
    parser = argparse.ArgumentParser(description="File Organizer — сортировщик файлов по папкам")
    parser.add_argument("folder", nargs="?", help="Путь к папке для организации")
    parser.add_argument("--preview", action="store_true", help="Показать план без реальных изменений")
    parser.add_argument("--undo", action="store_true", help="Отменить последнюю организацию")

    args = parser.parse_args()

    if args.undo:
        undo()
        return

    if not args.folder:
        print("Ошибка: укажи путь к папке. Например: python main.py ~/Downloads")
        return

    if not validate_folder(args.folder):
        return

    try:
        config = load_config()
    except FileNotFoundError:
        print("Ошибка: файл config.json не найден рядом с программой.")
        return
    except json.JSONDecodeError:
        print("Ошибка: config.json повреждён — проверь синтаксис JSON.")
        return

    if args.preview:
        plan = build_plan(args.folder, config)
        print_plan(plan)
        return

    results, errors = organize(args.folder, config)

    save_log(results, args.folder)

    print(f"🗂 Организация завершена! Обработано файлов: {len(results)}")
    for source, destination in results:
        print(f"  {source.name} → {destination.parent.name}/{destination.name}")

    if errors:
        print(f"⚠️ Не удалось переместить: {len(errors)}")
        for source, error in errors:
            print(f"  {source.name}: {error}")

if __name__ == "__main__":
    main()