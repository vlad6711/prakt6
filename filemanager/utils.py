import os
import shutil
from pathlib import Path
from typing import Union
from .exceptions import OutsideWorkspaceError


def validate_path(workspace: str, path: Union[str, Path]) -> Path:
    """Проверяет, что путь находится внутри рабочей директории"""
    workspace = Path(workspace).resolve()
    full_path = (workspace / path).resolve()

    try:
        full_path.relative_to(workspace)
    except ValueError:
        raise OutsideWorkspaceError(f"Путь {full_path} находится вне рабочей директории {workspace}")

    return full_path


def copy_file(src: Path, dst: Path):
    """Копирует файл с проверками"""
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def move_file(src: Path, dst: Path):
    """Перемещает файл с проверками"""
    shutil.move(src, dst)