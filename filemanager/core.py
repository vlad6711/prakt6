import os
import shutil
from pathlib import Path
from typing import List
from .utils import validate_path, copy_file, move_file
from .exceptions import *


class FileManager:
    def __init__(self, workspace: str):
        self.workspace = Path(workspace).resolve()
        self.current_dir = Path('')

        if not self.workspace.exists():
            raise FileNotFoundError(f"Рабочая директория {self.workspace} не существует")

    def execute(self, command: str):
        parts = command.split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        try:
            if cmd == 'help':
                self._help()
            elif cmd == 'ls':
                self._list_contents()
            elif cmd == 'cd':
                self._change_dir(args)
            elif cmd == 'mkdir':
                self._make_dir(args)
            elif cmd == 'rmdir':
                self._remove_dir(args)
            elif cmd == 'touch':
                self._create_file(args)
            elif cmd == 'rm':
                self._remove_file(args)
            elif cmd == 'cat':
                self._read_file(args)
            elif cmd == 'write':
                self._write_file(args)
            elif cmd == 'cp':
                self._copy_file(args)
            elif cmd == 'mv':
                self._move_rename(args)
            elif cmd == 'pwd':
                self._show_current_path()
            else:
                raise InvalidCommandError(f"Неизвестная команда: {cmd}")
        except FileManagerError as e:
            print(f"Ошибка: {e}")

    def _help(self):
        commands = {
            'help': 'Показать это сообщение',
            'ls': 'Показать содержимое текущей директории',
            'cd <dir>': 'Перейти в директорию',
            'mkdir <dir>': 'Создать директорию',
            'rmdir <dir>': 'Удалить директорию',
            'touch <file>': 'Создать файл',
            'rm <file>': 'Удалить файл',
            'cat <file>': 'Показать содержимое файла',
            'write <file> <text>': 'Записать текст в файл',
            'cp <src> <dst>': 'Копировать файл/директорию',
            'mv <src> <dst>': 'Переместить или переименовать файл/директорию',
            'pwd': 'Показать текущий путь',
            'exit': 'Выйти из программы'
        }

        print("Доступные команды:")
        for cmd, desc in commands.items():
            print(f"  {cmd:15} - {desc}")

    def _list_contents(self):
        path = self._get_full_path(self.current_dir)
        items = os.listdir(path)

        dirs = [f"{item}/" for item in items if (path / item).is_dir()]
        files = [item for item in items if (path / item).is_file()]

        print("\n".join(sorted(dirs) + sorted(files)))

    def _change_dir(self, args: List[str]):
        if not args:
            print(f"Текущая директория: {self.current_dir}")
            return

        new_dir = args[0]
        new_path = self._get_full_path(self.current_dir / new_dir)

        if not new_path.is_dir():
            raise FileSystemError(f"Директория {new_dir} не существует")

        self.current_dir = (self.current_dir / new_dir).resolve().relative_to(self.workspace)

    def _make_dir(self, args: List[str]):
        if not args:
            raise InvalidCommandError("Не указано имя директории")

        for dir_name in args:
            new_dir = self._get_full_path(self.current_dir / dir_name)
            try:
                new_dir.mkdir(exist_ok=False)
                print(f"Создана директория: {dir_name}")
            except FileExistsError:
                raise FileSystemError(f"Директория {dir_name} уже существует")

    def _remove_dir(self, args: List[str]):
        if not args:
            raise InvalidCommandError("Не указано имя директории")

        for dir_name in args:
            dir_path = self._get_full_path(self.current_dir / dir_name)
            if not dir_path.is_dir():
                raise FileSystemError(f"Директория {dir_name} не существует")

            try:
                dir_path.rmdir()
                print(f"Директория {dir_name} удалена")
            except OSError:
                raise FileSystemError(f"Директория {dir_name} не пуста. Используйте 'rm -r' для рекурсивного удаления")

    def _create_file(self, args: List[str]):
        if not args:
            raise InvalidCommandError("Не указано имя файла")

        for file_name in args:
            file_path = self._get_full_path(self.current_dir / file_name)
            if file_path.exists():
                raise FileSystemError(f"Файл {file_name} уже существует")

            file_path.touch()
            print(f"Создан файл: {file_name}")

    def _remove_file(self, args: List[str]):
        if not args:
            raise InvalidCommandError("Не указано имя файла")

        for file_name in args:
            file_path = self._get_full_path(self.current_dir / file_name)
            if not file_path.is_file():
                raise FileSystemError(f"Файл {file_name} не существует")

            file_path.unlink()
            print(f"Файл {file_name} удален")

    def _read_file(self, args: List[str]):
        if not args:
            raise InvalidCommandError("Не указано имя файла")

        file_name = args[0]
        file_path = self._get_full_path(self.current_dir / file_name)

        if not file_path.is_file():
            raise FileSystemError(f"Файл {file_name} не существует")

        with open(file_path, 'r') as f:
            print(f.read())

    def _write_file(self, args: List[str]):
        if len(args) < 2:
            raise InvalidCommandError("Не указано имя файла или текст для записи")

        file_name = args[0]
        text = ' '.join(args[1:])
        file_path = self._get_full_path(self.current_dir / file_name)

        with open(file_path, 'w') as f:
            f.write(text)
        print(f"Текст записан в файл {file_name}")

    def _copy_file(self, args: List[str]):
        if len(args) != 2:
            raise InvalidCommandError("Необходимо указать источник и назначение")

        src = args[0]
        dst = args[1]

        src_path = self._get_full_path(self.current_dir / src)
        dst_path = self._get_full_path(self.current_dir / dst)

        if not src_path.exists():
            raise FileSystemError(f"Источник {src} не существует")

        copy_file(src_path, dst_path)
        print(f"Скопировано {src} -> {dst}")

    def _move_rename(self, args: List[str]):
        if len(args) != 2:
            raise InvalidCommandError("Необходимо указать источник и назначение")

        src = args[0]
        dst = args[1]

        src_path = self._get_full_path(self.current_dir / src)
        dst_path = self._get_full_path(self.current_dir / dst)

        if not src_path.exists():
            raise FileSystemError(f"Источник {src} не существует")

        move_file(src_path, dst_path)
        print(f"Перемещено/переименовано {src} -> {dst}")

    def _show_current_path(self):
        print(str(self.current_dir))

    def _get_full_path(self, path: Path) -> Path:
        return validate_path(self.workspace, path)