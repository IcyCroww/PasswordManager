import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import PasswordManagerWindow, MasterPasswordDialog  # Правильное имя
from storage import StorageManager

DB_PATH = "vault.db"

def main():
    app = QApplication(sys.argv)
    storage = StorageManager(DB_PATH)

    if not storage.exists():
        print("📁 Создание НОВОЙ базы данных...")
        dialog = MasterPasswordDialog(is_new=True)
        if dialog.exec() and dialog.password:
            storage.initialize(dialog.password)
        else:
            return
    else:
        print("📁 База данных существует, разблокировка...")
        dialog = MasterPasswordDialog(is_new=False)
        if dialog.exec() and dialog.password:
            if not storage.unlock(dialog.password):
                QMessageBox.critical(None, "Ошибка",
                    "Неверный мастер-пароль!")
                return
        else:
            return

    window = PasswordManagerWindow(storage)  # Используем правильное имя
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()