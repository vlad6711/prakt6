import os
from filemanager.core import FileManager
import config


def main():
    workspace = os.path.expanduser(config.directory)

    os.makedirs(workspace, exist_ok=True)

    fm = FileManager(workspace)

    print(f"Рабочая директория: {workspace}")
    print("Введите 'help' для списка команд")

    while True:
        try:
            command = input(f"{fm.current_dir}> ").strip()
            if not command:
                continue

            if command.lower() == 'exit':
                break

            fm.execute(command)

        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit'")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()