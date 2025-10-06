# models.py
from dataclasses import dataclass

@dataclass
class PasswordEntry:
    site: str
    username: str
    password: str
