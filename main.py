#!/usr/bin/env python3
# main.py - Точка входа с повторными попытками
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

DB_PATH = "vault.db"
MAX_ATTEMPTS = 3  # Максимум попыток ввода пароля


def main():
    """Главная функция запуска приложения"""

    print("🚀 Запуск Password Manager...")
    print(f"📁 Путь к БД: {DB_PATH}\n")

    # Создаём приложение
    app = QApplication(sys.argv)
    app.setApplicationName("Password Manager")
    app.setOrganizationName("SecureVault")

    # Убираем обводки
    try:
        app.setStyle('Fusion')
        app.setStyleSheet("""
            * { outline: 0 !important; }
            *:focus { outline: 0 !important; }
        """)
        print("✅ Fusion стиль применён\n")
    except Exception as e:
        print(f"⚠️  Не удалось применить стиль: {e}\n")

    try:
        # Импорты
        print("📦 Загрузка модулей...")
        from gui import PasswordManagerWindow, MasterPasswordDialog
        from storage import StorageManager
        print("✅ Модули загружены\n")

        # Создаём хранилище
        storage = StorageManager(DB_PATH)

        if not storage.exists():
            # ========== СОЗДАНИЕ НОВОЙ БД ==========
            print("📦 Создание новой базы данных...\n")

            attempts = 0
            while attempts < MAX_ATTEMPTS:
                attempts += 1
                print(f"🔐 Попытка создания {attempts}/{MAX_ATTEMPTS}")

                dialog = MasterPasswordDialog(is_new=True)
                result = dialog.exec()

                if result and dialog.password:
                    print(f"   Пароль введён (длина: {len(dialog.password)} символов)")

                    if storage.initialize(dialog.password):
                        print("   ✅ База создана успешно!\n")
                        break
                    else:
                        QMessageBox.critical(None, "Ошибка",
                                             "❌ Не удалось создать базу!\n\nПроверьте права доступа.")
                        print("   ❌ Ошибка создания\n")
                        return 1
                else:
                    print("   ⚠️  Отменено пользователем")

                    if attempts < MAX_ATTEMPTS:
                        reply = QMessageBox.question(
                            None,
                            "Подтверждение",
                            f"Вы уверены что хотите выйти?\n\n"
                            f"Осталось попыток: {MAX_ATTEMPTS - attempts}",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )

                        if reply == QMessageBox.StandardButton.Yes:
                            print("   ❌ Выход подтверждён\n")
                            return 0
                        else:
                            print("   🔄 Попробуйте снова\n")
                            continue
                    else:
                        print("   ❌ Превышено количество попыток\n")
                        return 0

            if not storage.key:
                print("❌ База не создана после всех попыток\n")
                return 0

        else:
            # ========== ОТКРЫТИЕ СУЩЕСТВУЮЩЕЙ БД ==========
            print("🔓 Открытие существующей базы...\n")

            attempts = 0
            while attempts < MAX_ATTEMPTS:
                attempts += 1
                print(f"🔐 Попытка входа {attempts}/{MAX_ATTEMPTS}")

                dialog = MasterPasswordDialog(is_new=False)
                result = dialog.exec()

                if result and dialog.password:
                    print(f"   Попытка разблокировки (длина: {len(dialog.password)} символов)")

                    if storage.unlock(dialog.password):
                        print("   ✅ Пароль верный!\n")
                        break
                    else:
                        print("   ❌ Неверный пароль")

                        remaining = MAX_ATTEMPTS - attempts

                        if remaining > 0:
                            QMessageBox.warning(
                                None,
                                "Неверный пароль",
                                f"❌ Неверный мастер-пароль!\n\n"
                                f"Осталось попыток: {remaining}\n\n"
                                f"Попробуйте снова."
                            )
                            print(f"   Осталось попыток: {remaining}\n")
                        else:
                            QMessageBox.critical(
                                None,
                                "Доступ заблокирован",
                                "❌ Превышено количество попыток!\n\n"
                                "Попробуйте позже."
                            )
                            print("   ❌ Превышено количество попыток\n")
                            return 1
                else:
                    print("   ⚠️  Отменено пользователем")

                    reply = QMessageBox.question(
                        None,
                        "Подтверждение",
                        "Вы уверены что хотите выйти?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )

                    if reply == QMessageBox.StandardButton.Yes:
                        print("   ❌ Выход подтверждён\n")
                        return 0
                    else:
                        print("   🔄 Попробуйте снова\n")
                        continue

            if storage.is_locked():
                print("❌ База не разблокирована после всех попыток\n")
                return 0

        # ========== ЗАПУСК ГЛАВНОГО ОКНА ==========
        print("🎨 Загрузка интерфейса...\n")

        window = PasswordManagerWindow(storage)
        window.show()

        print("✅ Приложение запущено успешно!\n")
        print("=" * 50)
        print("💡 Приложение работает...")
        print("💡 Нажмите Ctrl+C в консоли для остановки")
        print("=" * 50 + "\n")

        # Запуск event loop
        exit_code = app.exec()

        # Закрываем хранилище при выходе
        print("\n" + "=" * 50)
        print("Завершение работы...")
        print("=" * 50)

        storage.close()
        print("✅ Хранилище закрыто")
        print("👋 Выход из приложения\n")

        return exit_code

    except ImportError as e:
        print(f"\n💥 ОШИБКА ИМПОРТА:")
        print(f"   {e}")
        print(f"\n📋 Проверьте что все файлы на месте:")
        print("   - gui.py")
        print("   - storage.py")
        print("   - models.py")
        print("   - generator.py")
        print("   - crypto_utils.py\n")

        QMessageBox.critical(None, "Ошибка импорта",
                             f"Не удалось загрузить модули:\n\n{str(e)}\n\nПроверьте что все файлы на месте.")

        traceback.print_exc()
        return 1

    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА:")
        print(f"   {e}\n")

        print("📋 Полный traceback:")
        traceback.print_exc()

        QMessageBox.critical(None, "Критическая ошибка",
                             f"Произошла критическая ошибка:\n\n{str(e)}\n\nПроверьте консоль для деталей.")

        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем (Ctrl+C)")
        print("👋 Выход...\n")
        sys.exit(0)