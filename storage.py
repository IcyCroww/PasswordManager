# storage.py - Безопасное хранилище паролей
import sqlite3
import os
from typing import Optional, List
from datetime import datetime
from models import PasswordEntry
from crypto_utils import CryptoUtils


class StorageManager:
    """Менеджер хранилища с шифрованием"""

    DB_VERSION = 2  # Версия схемы БД

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.key: Optional[bytes] = None
        self.salt: Optional[bytes] = None
        self._is_locked = True

    def exists(self) -> bool:
        """Проверка существования БД"""
        return os.path.exists(self.db_path)

    def initialize(self, master_password: str) -> bool:
        """Создание новой зашифрованной БД"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cur = self.conn.cursor()

            # Генерируем соль
            self.salt = CryptoUtils.generate_salt()

            # Создаём ключ
            self.key = CryptoUtils.derive_key(master_password, self.salt)

            # Создаём таблицы
            cur.execute("""
                CREATE TABLE meta (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password BLOB NOT NULL,
                    notes BLOB,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(site, username)
                )
            """)

            # Индексы для быстрого поиска
            cur.execute("CREATE INDEX idx_site ON vault(site)")
            cur.execute("CREATE INDEX idx_username ON vault(username)")

            # Сохраняем метаданные
            cur.execute("INSERT INTO meta VALUES ('salt', ?)", (self.salt,))
            cur.execute("INSERT INTO meta VALUES ('version', ?)",
                        (str(self.DB_VERSION).encode(),))

            # Создаём проверочную запись для валидации пароля
            verification = CryptoUtils.generate_secure_token(16)
            encrypted_verification = CryptoUtils.encrypt(self.key, verification)
            cur.execute("INSERT INTO meta VALUES ('verification', ?)",
                        (encrypted_verification,))

            self.conn.commit()
            self._is_locked = False

            print(f"✅ База данных создана: {self.db_path}")
            return True

        except Exception as e:
            print(f"❌ Ошибка создания БД: {e}")
            if self.conn:
                self.conn.close()
            self.conn = None
            self.key = None
            return False

    def unlock(self, master_password: str) -> bool:
        """Разблокировка существующей БД"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cur = self.conn.cursor()

            # Загружаем соль
            cur.execute("SELECT value FROM meta WHERE key = 'salt'")
            row = cur.fetchone()
            if not row:
                raise ValueError("Повреждённая БД: нет соли")

            self.salt = row['value']

            # Создаём ключ
            self.key = CryptoUtils.derive_key(master_password, self.salt)

            # Проверяем правильность пароля через verification
            cur.execute("SELECT value FROM meta WHERE key = 'verification'")
            row = cur.fetchone()
            if not row:
                raise ValueError("Повреждённая БД: нет верификации")

            try:
                CryptoUtils.decrypt(self.key, row['value'])
                self._is_locked = False
                print("✅ База данных разблокирована")
                return True
            except:
                self.key = None
                print("❌ Неверный пароль")
                return False

        except Exception as e:
            print(f"❌ Ошибка открытия БД: {e}")
            if self.conn:
                self.conn.close()
            self.conn = None
            self.key = None
            return False

    def add_password(self, entry: PasswordEntry) -> bool:
        """Добавление нового пароля"""
        if not self.key or self._is_locked:
            print("❌ БД заблокирована")
            return False

        try:
            encrypted_password = CryptoUtils.encrypt(self.key, entry.password)
            encrypted_notes = None
            if entry.notes:
                encrypted_notes = CryptoUtils.encrypt(self.key, entry.notes)

            now = datetime.now().isoformat()

            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO vault (site, username, password, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entry.site, entry.username, encrypted_password, encrypted_notes, now, now))

            self.conn.commit()
            print(f"✅ Пароль добавлен: {entry.site}")
            return True

        except sqlite3.IntegrityError:
            print(f"⚠️ Пароль для {entry.site} ({entry.username}) уже существует")
            return False
        except Exception as e:
            print(f"❌ Ошибка добавления: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_all_passwords(self) -> List[PasswordEntry]:
        """Получение всех паролей"""
        if not self.key or self._is_locked:
            return []

        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT site, username, password, notes, created_at, updated_at 
                FROM vault 
                ORDER BY site ASC
            """)

            result = []
            for row in cur.fetchall():
                try:
                    password = CryptoUtils.decrypt(self.key, row['password'])
                    notes = None
                    if row['notes']:
                        notes = CryptoUtils.decrypt(self.key, row['notes'])

                    result.append(PasswordEntry(
                        site=row['site'],
                        username=row['username'],
                        password=password,
                        notes=notes,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except Exception as e:
                    print(f"⚠️ Ошибка расшифровки записи {row['site']}: {e}")
                    continue

            print(f"✅ Загружено паролей: {len(result)}")
            return result

        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return []

    def update_password(self, site: str, username: str, new_entry: PasswordEntry) -> bool:
        """Обновление существующего пароля"""
        if not self.key or self._is_locked:
            return False

        try:
            encrypted_password = CryptoUtils.encrypt(self.key, new_entry.password)
            encrypted_notes = None
            if new_entry.notes:
                encrypted_notes = CryptoUtils.encrypt(self.key, new_entry.notes)

            now = datetime.now().isoformat()

            cur = self.conn.cursor()
            cur.execute("""
                UPDATE vault 
                SET password = ?, notes = ?, updated_at = ?
                WHERE site = ? AND username = ?
            """, (encrypted_password, encrypted_notes, now, site, username))

            self.conn.commit()

            if cur.rowcount > 0:
                print(f"✅ Пароль обновлён: {site}")
                return True
            else:
                print(f"⚠️ Запись не найдена: {site}")
                return False

        except Exception as e:
            print(f"❌ Ошибка обновления: {e}")
            return False

    def delete_password(self, site: str, username: str) -> bool:
        """Удаление пароля"""
        if not self.key or self._is_locked:
            return False

        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM vault WHERE site = ? AND username = ?",
                        (site, username))
            self.conn.commit()

            if cur.rowcount > 0:
                print(f"✅ Пароль удалён: {site}")
                return True
            else:
                print(f"⚠️ Запись не найдена: {site}")
                return False

        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False

    def search_passwords(self, query: str) -> List[PasswordEntry]:
        """Поиск паролей по сайту или логину"""
        if not self.key or self._is_locked:
            return []

        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT site, username, password, notes, created_at, updated_at 
                FROM vault 
                WHERE site LIKE ? OR username LIKE ?
                ORDER BY site ASC
            """, (f"%{query}%", f"%{query}%"))

            result = []
            for row in cur.fetchall():
                try:
                    password = CryptoUtils.decrypt(self.key, row['password'])
                    notes = None
                    if row['notes']:
                        notes = CryptoUtils.decrypt(self.key, row['notes'])

                    result.append(PasswordEntry(
                        site=row['site'],
                        username=row['username'],
                        password=password,
                        notes=notes,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except:
                    continue

            return result

        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []

    def get_stats(self) -> dict:
        """Получение статистики"""
        if not self.conn or self._is_locked:
            return {"total": 0, "sites": 0}

        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) as total, COUNT(DISTINCT site) as sites FROM vault")
            row = cur.fetchone()

            return {
                "total": row['total'],
                "sites": row['sites']
            }
        except:
            return {"total": 0, "sites": 0}

    def lock(self):
        """Блокировка БД (очистка ключа из памяти)"""
        self.key = None
        self._is_locked = True
        print("🔒 База данных заблокирована")

    def close(self):
        """Закрытие БД"""
        self.lock()
        if self.conn:
            self.conn.close()
            self.conn = None
        print("✅ Соединение закрыто")

    def is_locked(self) -> bool:
        """Проверка блокировки"""
        return self._is_locked