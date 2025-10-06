# storage.py
import sqlite3
import os
from models import PasswordEntry
from crypto_utils import CryptoUtils


class StorageManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.key = None
        self.salt = None

    def exists(self) -> bool:
        return os.path.exists(self.db_path)

    def initialize(self, master_password: str):
        try:
            self.conn = sqlite3.connect(self.db_path)
            cur = self.conn.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS meta (salt BLOB)")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password BLOB NOT NULL
                )
            """)

            self.salt = os.urandom(32)
            cur.execute("INSERT INTO meta VALUES (?)", (self.salt,))
            self.key = CryptoUtils.derive_key(master_password, self.salt)

            # Тестовая запись
            test_encrypted = CryptoUtils.encrypt(self.key, "test_verification")
            cur.execute("INSERT INTO vault VALUES (?, ?, ?, ?)",
                        (None, "__test__", "test", test_encrypted))

            self.conn.commit()
            print("✓ База создана")
            return True

        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return False

    def unlock(self, master_password: str) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_path)
            cur = self.conn.cursor()

            cur.execute("SELECT salt FROM meta LIMIT 1")
            row = cur.fetchone()
            if not row:
                return False

            self.salt = row[0]
            self.key = CryptoUtils.derive_key(master_password, self.salt)

            # Проверка пароля
            cur.execute("SELECT password FROM vault WHERE site = ?", ("__test__",))
            test_row = cur.fetchone()

            if test_row:
                try:
                    decrypted = CryptoUtils.decrypt(self.key, test_row[0])
                    if decrypted != "test_verification":
                        self.key = None
                        return False
                    print("✓ Вход выполнен")
                    return True
                except:
                    self.key = None
                    return False
            return False

        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return False

    def add_password(self, entry: PasswordEntry):
        if not self.key:
            return False

        try:
            encrypted_pwd = CryptoUtils.encrypt(self.key, entry.password)

            cur = self.conn.cursor()
            # username НЕ шифруем - храним как есть
            cur.execute("INSERT INTO vault VALUES (?, ?, ?, ?)",
                        (None, entry.site, entry.username, encrypted_pwd))
            self.conn.commit()

            cur.execute("SELECT COUNT(*) FROM vault WHERE site != ?", ("__test__",))
            count = cur.fetchone()[0]
            print(f"✓ Сохранено! Всего: {count}")
            return True

        except Exception as e:
            print(f"✗ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_all_passwords(self) -> list:
        if not self.key:
            return []

        try:
            cur = self.conn.cursor()
            cur.execute("SELECT site, username, password FROM vault WHERE site != ?",
                        ("__test__",))
            rows = cur.fetchall()

            result = []
            for site, username, encrypted in rows:
                try:
                    # username НЕ расшифровываем - он не зашифрован
                    pw = CryptoUtils.decrypt(self.key, encrypted)
                    result.append(PasswordEntry(site, username, pw))
                except Exception as e:
                    print(f"⚠ Ошибка: {e}")
                    continue

            print(f"✓ Загружено: {len(result)}")
            return result

        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return []

    def delete_password(self, site: str, username: str) -> bool:
        if not self.key:
            return False

        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM vault WHERE site = ? AND username = ?",
                        (site, username))
            self.conn.commit()
            print(f"✓ Удалено: {site}")
            return True
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return False

    def search_passwords(self, site: str) -> list:
        if not self.key:
            return []

        try:
            cur = self.conn.cursor()
            cur.execute("SELECT site, username, password FROM vault WHERE site LIKE ? AND site != ?",
                        (f"%{site}%", "__test__"))
            rows = cur.fetchall()

            return [
                PasswordEntry(site, username, CryptoUtils.decrypt(self.key, encrypted))
                for site, username, encrypted in rows
            ]
        except:
            return []

    def close(self):
        if self.conn:
            self.conn.close()
        self.key = None
        self.salt = None