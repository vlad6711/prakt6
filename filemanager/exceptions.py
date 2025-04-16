class FileManagerError(Exception):
    """Базовое исключение для файлового менеджера"""
    pass

class OutsideWorkspaceError(FileManagerError):
    """Попытка выйти за пределы рабочей директории"""
    pass

class InvalidCommandError(FileManagerError):
    """Некорректная команда"""
    pass

class FileSystemError(FileManagerError):
    """Ошибка файловой системы"""
    pass