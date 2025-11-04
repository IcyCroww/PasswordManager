# models.py - Модели данных
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class PasswordEntry:
    """Запись пароля в хранилище"""
    site: str
    username: str
    password: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Автоматическая установка временных меток"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()