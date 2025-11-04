# gui.py - ИДЕАЛЬНЫЙ GUI БЕЗ ЕБУЧИХ ВЫДЕЛЕНИЙ
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QSize, QEvent
from PyQt6.QtGui import QFont, QPalette, QColor

from storage import StorageManager
from generator import PasswordGenerator
from models import PasswordEntry

# ============= ИДЕАЛЬНАЯ ТЁМНАЯ ТЕМА (GitHub Style) =============
PERFECT_THEME = """
/* ГЛОБАЛЬНОЕ ОТКЛЮЧЕНИЕ ВСЕХ ОБВОДОК */
* {
    outline: none;
    border: none;
}

*:focus {
    outline: none !important;
    border: none;
}

QWidget:focus, QPushButton:focus, QLineEdit:focus, QTextEdit:focus,
QCheckBox:focus, QSlider:focus, QComboBox:focus {
    outline: none !important;
}

/* БАЗОВЫЕ ЭЛЕМЕНТЫ */
QMainWindow, QDialog, QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
    font-size: 14px;
}

/* НАВИГАЦИОННАЯ ПАНЕЛЬ */
QFrame#nav_panel {
    background-color: #161b22;
    border-radius: 12px;
    border: 1px solid #30363d;
}

QPushButton#nav_button {
    background-color: transparent;
    color: #7d8590;
    border: none;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    border-radius: 6px;
    margin: 2px 0px;
}

QPushButton#nav_button:hover {
    background-color: #21262d;
    color: #c9d1d9;
}

QPushButton#nav_button:checked {
    background-color: #388bfd1a;
    color: #58a6ff;
    font-weight: 600;
}

/* КНОПКИ */
QPushButton {
    background-color: #238636;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2ea043;
}

QPushButton:pressed {
    background-color: #1a7f37;
}

QPushButton:disabled {
    background-color: #21262d;
    color: #484f58;
}

QPushButton#secondary {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #c9d1d9;
}

QPushButton#secondary:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

QPushButton#danger {
    background-color: #da3633;
    color: #ffffff;
}

QPushButton#danger:hover {
    background-color: #f85149;
}

/* ПОЛЯ ВВОДА */
QLineEdit, QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #c9d1d9;
    font-size: 14px;
    selection-background-color: #1f6feb;
}

QLineEdit:hover, QTextEdit:hover {
    border-color: #6e7681;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #1f6feb;
    padding: 7px 11px;
    background-color: #0d1117;
}

/* ЧЕКБОКСЫ (БЕЗ ВЫДЕЛЕНИЯ!!!) */
QCheckBox {
    spacing: 10px;
    color: #c9d1d9;
    padding: 4px;
}

QCheckBox:hover {
    color: #f0f6fc;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #6e7681;
    border-radius: 3px;
    background-color: #0d1117;
}

QCheckBox::indicator:hover {
    border-color: #8b949e;
    background-color: #161b22;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
    image: none;
}

QCheckBox::indicator:checked:hover {
    background-color: #388bfd;
    border-color: #388bfd;
}

QCheckBox::indicator:disabled {
    border-color: #30363d;
    background-color: #161b22;
}

/* СЛАЙДЕРЫ */
QSlider {
    min-height: 20px;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #21262d;
    border-radius: 2px;
    margin: 8px 0;
}

QSlider::handle:horizontal {
    background: #1f6feb;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
    border: none;
}

QSlider::handle:horizontal:hover {
    background: #388bfd;
}

QSlider::handle:horizontal:pressed {
    background: #1f6feb;
}

QSlider::handle:horizontal:focus {
    background: #1f6feb;
    border: none;
    outline: none;
}

/* ПРОГРЕСС БАР */
QProgressBar {
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #161b22;
    text-align: center;
    height: 8px;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #238636;
    border-radius: 3px;
}

/* КАРТОЧКИ */
QFrame#card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px;
}

QFrame#card:hover {
    border-color: #8b949e;
}

QFrame#password_card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
}

QFrame#password_card:hover {
    background-color: #1c2128;
    border-color: #58a6ff;
}

/* ЛЕЙБЛЫ */
QLabel#title {
    font-size: 32px;
    font-weight: 600;
    color: #f0f6fc;
    padding: 0px;
}

QLabel#subtitle {
    font-size: 14px;
    color: #7d8590;
}

QLabel#section_title {
    font-size: 14px;
    font-weight: 600;
    color: #f0f6fc;
    margin-bottom: 8px;
}

/* СКРОЛЛ */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

/* ДИАЛОГИ */
QDialog {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}

QMessageBox {
    background-color: #161b22;
}

QMessageBox QLabel {
    color: #c9d1d9;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 8px 16px;
}

/* РАЗДЕЛИТЕЛИ */
QFrame[frameShape="4"] {
    background-color: #21262d;
    max-height: 1px;
}
"""


class NoFocusCheckBox(QCheckBox):
    """Чекбокс без фокуса и без выделения"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)


class NoFocusSlider(QSlider):
    """Слайдер без фокуса"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


# ============= ДИАЛОГИ =============

class MasterPasswordDialog(QDialog):
    """Диалог мастер-пароля"""

    def __init__(self, is_new: bool = False, parent=None):
        super().__init__(parent)
        self.is_new = is_new
        self.password = None
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Мастер-пароль")
        self.setModal(True)
        self.setFixedWidth(480)
        self.setStyleSheet(PERFECT_THEME)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        if self.is_new:
            title = QLabel("🔐 Создание хранилища")
            desc = QLabel("Придумайте надёжный мастер-пароль\n⚠️ Восстановление невозможно!")
        else:
            title = QLabel("🔓 Вход")
            desc = QLabel("Введите мастер-пароль для доступа")

        title.setObjectName("title")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc.setObjectName("subtitle")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль...")
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)

        if self.is_new:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setPlaceholderText("Повторите пароль...")
            self.confirm_input.setMinimumHeight(40)
            layout.addWidget(self.confirm_input)

        layout.addSpacing(8)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Продолжить" if self.is_new else "Войти")
        ok_btn.setMinimumHeight(40)
        ok_btn.clicked.connect(self.validate)
        ok_btn.setDefault(True)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def validate(self):
        pwd = self.password_input.text()

        if not pwd:
            QMessageBox.warning(self, "Ошибка", "Введите пароль!")
            return

        if self.is_new:
            if len(pwd) < 8:
                QMessageBox.warning(self, "Ошибка",
                                    "Пароль должен содержать минимум 8 символов!")
                return

            if pwd != self.confirm_input.text():
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
                return

        self.password = pwd
        self.accept()


class AddPasswordDialog(QDialog):
    """Диалог добавления пароля"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = None
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить пароль")
        self.setModal(True)
        self.setFixedSize(560, 680)
        self.setStyleSheet(PERFECT_THEME)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Заголовок
        title = QLabel("Новая запись")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")
        layout.addWidget(title)

        layout.addSpacing(8)

        # Сайт
        site_label = QLabel("🌐 Сайт")
        site_label.setObjectName("section_title")
        layout.addWidget(site_label)

        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("example.com")
        self.site_input.setMinimumHeight(36)
        layout.addWidget(self.site_input)

        # Логин
        user_label = QLabel("👤 Имя пользователя")
        user_label.setObjectName("section_title")
        layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("user@example.com")
        self.username_input.setMinimumHeight(36)
        layout.addWidget(self.username_input)

        # Пароль
        pwd_label = QLabel("🔒 Пароль")
        pwd_label.setObjectName("section_title")
        layout.addWidget(pwd_label)

        pwd_layout = QHBoxLayout()
        pwd_layout.setSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите или сгенерируйте пароль")
        self.password_input.setMinimumHeight(36)
        self.password_input.textChanged.connect(self.update_strength)
        pwd_layout.addWidget(self.password_input)

        self.show_btn = QPushButton("👁")
        self.show_btn.setObjectName("secondary")
        self.show_btn.setFixedSize(36, 36)
        self.show_btn.setToolTip("Показать пароль")
        self.show_btn.clicked.connect(self.toggle_visibility)
        pwd_layout.addWidget(self.show_btn)

        layout.addLayout(pwd_layout)

        # Индикатор силы
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setFixedHeight(4)
        layout.addWidget(self.strength_bar)

        self.strength_label = QLabel("")
        self.strength_label.setObjectName("subtitle")
        self.strength_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.strength_label)

        layout.addSpacing(8)

        # Генератор
        gen_frame = QFrame()
        gen_frame.setObjectName("card")
        gen_layout = QVBoxLayout()
        gen_layout.setSpacing(12)

        gen_title = QLabel("⚡ Генератор паролей")
        gen_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #58a6ff;")
        gen_layout.addWidget(gen_title)

        # Длина
        len_container = QHBoxLayout()
        len_container.setSpacing(12)

        len_label = QLabel("Длина:")
        len_label.setStyleSheet("color: #7d8590; min-width: 50px;")
        len_container.addWidget(len_label)

        self.length_slider = NoFocusSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(8, 48)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length)
        len_container.addWidget(self.length_slider)

        self.length_label = QLabel("16")
        self.length_label.setStyleSheet("font-weight: 600; min-width: 25px;")
        len_container.addWidget(self.length_label)

        gen_layout.addLayout(len_container)

        # Опции
        opt_container = QVBoxLayout()
        opt_container.setSpacing(8)

        self.cb_upper = NoFocusCheckBox("Заглавные буквы (A-Z)")
        self.cb_upper.setChecked(True)
        opt_container.addWidget(self.cb_upper)

        self.cb_lower = NoFocusCheckBox("Строчные буквы (a-z)")
        self.cb_lower.setChecked(True)
        opt_container.addWidget(self.cb_lower)

        self.cb_digits = NoFocusCheckBox("Цифры (0-9)")
        self.cb_digits.setChecked(True)
        opt_container.addWidget(self.cb_digits)

        self.cb_symbols = NoFocusCheckBox("Символы (!@#$%^&*)")
        self.cb_symbols.setChecked(True)
        opt_container.addWidget(self.cb_symbols)

        gen_layout.addLayout(opt_container)

        gen_btn = QPushButton("🎲 Сгенерировать пароль")
        gen_btn.setMinimumHeight(36)
        gen_btn.clicked.connect(self.generate_pwd)
        gen_layout.addWidget(gen_btn)

        gen_frame.setLayout(gen_layout)
        layout.addWidget(gen_frame)

        # Заметки
        notes_label = QLabel("📝 Заметки (опционально)")
        notes_label.setObjectName("section_title")
        layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Дополнительная информация...")
        self.notes_input.setMaximumHeight(70)
        layout.addWidget(self.notes_input)

        layout.addStretch()

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Сохранить")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save)
        save_btn.setDefault(True)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_length(self, val):
        self.length_label.setText(str(val))

    def toggle_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_btn.setText("🙈")
            self.show_btn.setToolTip("Скрыть пароль")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_btn.setText("👁")
            self.show_btn.setToolTip("Показать пароль")

    def generate_pwd(self):
        pwd = PasswordGenerator.generate(
            length=self.length_slider.value(),
            uppercase=self.cb_upper.isChecked(),
            lowercase=self.cb_lower.isChecked(),
            digits=self.cb_digits.isChecked(),
            symbols=self.cb_symbols.isChecked()
        )
        self.password_input.setText(pwd)

    def update_strength(self):
        pwd = self.password_input.text()
        if not pwd:
            self.strength_bar.setValue(0)
            self.strength_label.setText("")
            return

        level, percent, entropy = PasswordGenerator.estimate_strength(pwd)
        self.strength_bar.setValue(percent)
        self.strength_label.setText(f"{level} • {entropy:.0f} бит энтропии")

        if percent < 40:
            color = "#da3633"
        elif percent < 70:
            color = "#fb8500"
        else:
            color = "#238636"

        self.strength_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")

    def save(self):
        site = self.site_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        notes = self.notes_input.toPlainText().strip() or None

        if not site or not username or not password:
            QMessageBox.warning(self, "Ошибка",
                                "Заполните все обязательные поля (сайт, логин, пароль)!")
            return

        self.result = PasswordEntry(
            site=site,
            username=username,
            password=password,
            notes=notes
        )
        self.accept()


class PasswordCard(QFrame):
    """Карточка пароля"""

    def __init__(self, entry: PasswordEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.parent_window = parent
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.init_ui()

    def init_ui(self):
        self.setObjectName("password_card")
        self.setMinimumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # Инфо
        info = QVBoxLayout()
        info.setSpacing(4)

        site = QLabel(self.entry.site)
        site.setStyleSheet("font-size: 16px; font-weight: 600; color: #58a6ff;")
        info.addWidget(site)

        user = QLabel(f"👤 {self.entry.username}")
        user.setStyleSheet("font-size: 13px; color: #7d8590;")
        info.addWidget(user)

        pwd = QLabel("●●●●●●●●●●●●")
        pwd.setStyleSheet("font-size: 13px; color: #7d8590; letter-spacing: 2px;")
        info.addWidget(pwd)

        layout.addLayout(info, stretch=1)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        copy_btn = QPushButton("📋 Копировать")
        copy_btn.setObjectName("secondary")
        copy_btn.setFixedWidth(120)
        copy_btn.setMinimumHeight(32)
        copy_btn.clicked.connect(self.on_copy)
        btn_layout.addWidget(copy_btn)

        del_btn = QPushButton("🗑")
        del_btn.setObjectName("danger")
        del_btn.setFixedSize(32, 32)
        del_btn.setToolTip("Удалить")
        del_btn.clicked.connect(self.on_delete)
        btn_layout.addWidget(del_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def on_copy(self):
        if self.parent_window:
            self.parent_window.copy_password(self.entry.password, self.entry.site)

    def on_delete(self):
        if self.parent_window:
            self.parent_window.delete_password(self.entry.site, self.entry.username)


# ============= ГЛАВНОЕ ОКНО =============

class PasswordManagerWindow(QMainWindow):
    """Главное окно"""

    def __init__(self, storage: StorageManager):
        super().__init__()
        self.storage = storage
        self.clipboard_timer = None
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.init_ui()
        self.load_passwords()

    def init_ui(self):
        self.setWindowTitle("Password Manager")
        self.setGeometry(100, 100, 1200, 750)
        self.setStyleSheet(PERFECT_THEME)

        central = QWidget()
        self.setCentralWidget(central)

        main = QHBoxLayout()
        main.setSpacing(20)
        main.setContentsMargins(20, 20, 20, 20)

        # === ЛЕВАЯ ПАНЕЛЬ ===
        nav = QFrame()
        nav.setObjectName("nav_panel")
        nav.setFixedWidth(220)

        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(8)
        nav_layout.setContentsMargins(16, 20, 16, 20)

        # Лого
        logo = QLabel("🔐")
        logo.setFont(QFont("Segoe UI", 40))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(logo)

        app_title = QLabel("Password\nManager")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title.setStyleSheet("color: #f0f6fc;")
        nav_layout.addWidget(app_title)

        nav_layout.addSpacing(24)

        # Кнопки навигации
        self.nav_passwords = QPushButton("  🔒 Мои пароли")
        self.nav_passwords.setObjectName("nav_button")
        self.nav_passwords.setCheckable(True)
        self.nav_passwords.setChecked(True)
        self.nav_passwords.setMinimumHeight(40)
        self.nav_passwords.clicked.connect(lambda: self.switch_page(0))
        nav_layout.addWidget(self.nav_passwords)

        self.nav_generator = QPushButton("  ⚡ Генератор")
        self.nav_generator.setObjectName("nav_button")
        self.nav_generator.setCheckable(True)
        self.nav_generator.setMinimumHeight(40)
        self.nav_generator.clicked.connect(lambda: self.switch_page(1))
        nav_layout.addWidget(self.nav_generator)

        nav_layout.addStretch()

        # Статистика
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #0d1117; border-radius: 6px; padding: 8px;")
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(8, 8, 8, 8)

        self.stats_label = QLabel("Всего паролей: 0")
        self.stats_label.setStyleSheet("color: #7d8590; font-size: 12px;")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.stats_label)

        stats_frame.setLayout(stats_layout)
        nav_layout.addWidget(stats_frame)

        nav_layout.addSpacing(8)

        # Кнопка блокировки
        lock_btn = QPushButton("🔒 Заблокировать")
        lock_btn.setObjectName("danger")
        lock_btn.setMinimumHeight(40)
        lock_btn.clicked.connect(self.lock_app)
        nav_layout.addWidget(lock_btn)

        nav.setLayout(nav_layout)
        main.addWidget(nav)

        # === ПРАВАЯ ПАНЕЛЬ ===
        self.content = QStackedWidget()
        self.content.addWidget(self.create_passwords_page())
        self.content.addWidget(self.create_generator_page())

        main.addWidget(self.content, stretch=1)
        central.setLayout(main)

    def create_passwords_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        header = QHBoxLayout()
        header.setSpacing(16)

        title = QLabel("Мои пароли")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 28px;")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("➕ Добавить пароль")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.add_password)
        header.addWidget(add_btn)

        layout.addLayout(header)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по сайту или логину...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.filter_passwords)
        layout.addWidget(self.search_input)

        # Список паролей
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(8)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_container.setLayout(self.cards_layout)

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

        page.setLayout(layout)
        return page

    def create_generator_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        title = QLabel("Генератор паролей")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 28px;")
        layout.addWidget(title)

        # Результат
        result_frame = QFrame()
        result_frame.setObjectName("card")
        result_layout = QVBoxLayout()
        result_layout.setSpacing(12)

        result_label = QLabel("Сгенерированный пароль:")
        result_label.setObjectName("section_title")
        result_layout.addWidget(result_label)

        res_container = QHBoxLayout()
        res_container.setSpacing(8)

        self.gen_result = QLineEdit()
        self.gen_result.setReadOnly(True)
        self.gen_result.setPlaceholderText("Нажмите 'Генерировать'")
        self.gen_result.setMinimumHeight(48)
        self.gen_result.setFont(QFont("Consolas, Monaco, monospace", 14))
        self.gen_result.setStyleSheet("letter-spacing: 1px;")
        res_container.addWidget(self.gen_result)

        copy_btn = QPushButton("📋")
        copy_btn.setObjectName("secondary")
        copy_btn.setFixedSize(48, 48)
        copy_btn.setToolTip("Копировать")
        copy_btn.clicked.connect(self.copy_generated)
        res_container.addWidget(copy_btn)

        result_layout.addLayout(res_container)

        # Длина
        len_container = QHBoxLayout()
        len_container.setSpacing(12)

        len_label = QLabel("Длина пароля:")
        len_label.setStyleSheet("color: #7d8590; min-width: 100px;")
        len_container.addWidget(len_label)

        self.gen_length = NoFocusSlider(Qt.Orientation.Horizontal)
        self.gen_length.setRange(8, 64)
        self.gen_length.setValue(20)
        self.gen_length.valueChanged.connect(self.update_gen_length)
        len_container.addWidget(self.gen_length)

        self.gen_length_label = QLabel("20")
        self.gen_length_label.setStyleSheet("font-weight: 600; font-size: 16px; min-width: 35px;")
        len_container.addWidget(self.gen_length_label)

        result_layout.addLayout(len_container)

        # Опции
        opt_label = QLabel("Использовать символы:")
        opt_label.setObjectName("section_title")
        result_layout.addWidget(opt_label)

        self.gen_upper = NoFocusCheckBox("Заглавные буквы (A-Z)")
        self.gen_upper.setChecked(True)
        result_layout.addWidget(self.gen_upper)

        self.gen_lower = NoFocusCheckBox("Строчные буквы (a-z)")
        self.gen_lower.setChecked(True)
        result_layout.addWidget(self.gen_lower)

        self.gen_digits = NoFocusCheckBox("Цифры (0-9)")
        self.gen_digits.setChecked(True)
        result_layout.addWidget(self.gen_digits)

        self.gen_symbols = NoFocusCheckBox("Символы (!@#$%^&*)")
        self.gen_symbols.setChecked(True)
        result_layout.addWidget(self.gen_symbols)

        result_layout.addSpacing(8)

        gen_btn = QPushButton("🎲 Сгенерировать пароль")
        gen_btn.setMinimumHeight(48)
        gen_btn.clicked.connect(self.generate_password)
        result_layout.addWidget(gen_btn)

        self.gen_strength = QLabel("")
        self.gen_strength.setObjectName("subtitle")
        self.gen_strength.setStyleSheet("font-size: 13px; margin-top: 4px;")
        result_layout.addWidget(self.gen_strength)

        result_frame.setLayout(result_layout)
        layout.addWidget(result_frame)

        layout.addStretch()

        page.setLayout(layout)
        return page

    def switch_page(self, index):
        self.nav_passwords.setChecked(index == 0)
        self.nav_generator.setChecked(index == 1)
        self.content.setCurrentIndex(index)
        if index == 0:
            self.load_passwords()

    def load_passwords(self):
        # Очистка
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        passwords = self.storage.get_all_passwords()

        if not passwords:
            empty = QFrame()
            empty.setObjectName("card")
            empty.setMinimumHeight(200)

            empty_layout = QVBoxLayout()
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            empty_icon = QLabel("📭")
            empty_icon.setFont(QFont("Segoe UI", 48))
            empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(empty_icon)

            empty_text = QLabel("Нет паролей")
            empty_text.setStyleSheet("font-size: 18px; font-weight: 600; color: #f0f6fc;")
            empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(empty_text)

            empty_hint = QLabel("Нажмите '➕ Добавить пароль' для создания первой записи")
            empty_hint.setObjectName("subtitle")
            empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(empty_hint)

            empty.setLayout(empty_layout)
            self.cards_layout.addWidget(empty)
        else:
            for entry in passwords:
                card = PasswordCard(entry, self)
                self.cards_layout.addWidget(card)

        # Статистика
        stats = self.storage.get_stats()
        self.stats_label.setText(f"Всего паролей: {stats['total']}")

    def filter_passwords(self, query):
        query = query.lower()
        for i in range(self.cards_layout.count()):
            widget = self.cards_layout.itemAt(i).widget()
            if isinstance(widget, PasswordCard):
                visible = (query in widget.entry.site.lower() or
                           query in widget.entry.username.lower())
                widget.setVisible(visible)

    def add_password(self):
        dialog = AddPasswordDialog(self)
        if dialog.exec() and dialog.result:
            if self.storage.add_password(dialog.result):
                QMessageBox.information(self, "Успех",
                                        "✅ Пароль успешно сохранён!")
                self.load_passwords()
            else:
                QMessageBox.critical(self, "Ошибка",
                                     "❌ Не удалось сохранить пароль\n\nВозможно такая запись уже существует.")

    def copy_password(self, password, site):
        clipboard = QApplication.clipboard()
        clipboard.setText(password)

        QMessageBox.information(self, "Скопировано",
                                f"✅ Пароль для {site} скопирован в буфер обмена!\n\n"
                                f"⏱ Буфер будет автоматически очищен через 30 секунд")

        if self.clipboard_timer:
            self.clipboard_timer.stop()

        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(lambda: self.clear_clipboard(password))
        self.clipboard_timer.setSingleShot(True)
        self.clipboard_timer.start(30000)

    def clear_clipboard(self, original):
        clipboard = QApplication.clipboard()
        if clipboard.text() == original:
            clipboard.clear()

    def delete_password(self, site, username):
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены что хотите удалить пароль?\n\n"
            f"Сайт: {site}\n"
            f"Логин: {username}\n\n"
            f"⚠️ Это действие необратимо!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.storage.delete_password(site, username):
                QMessageBox.information(self, "Успех", "✅ Пароль удалён!")
                self.load_passwords()
            else:
                QMessageBox.critical(self, "Ошибка",
                                     "❌ Не удалось удалить пароль")

    def generate_password(self):
        pwd = PasswordGenerator.generate(
            length=self.gen_length.value(),
            uppercase=self.gen_upper.isChecked(),
            lowercase=self.gen_lower.isChecked(),
            digits=self.gen_digits.isChecked(),
            symbols=self.gen_symbols.isChecked()
        )

        self.gen_result.setText(pwd)

        level, percent, entropy = PasswordGenerator.estimate_strength(pwd)
        self.gen_strength.setText(f"{level} • {entropy:.0f} бит энтропии")

    def update_gen_length(self, val):
        self.gen_length_label.setText(str(val))

    def copy_generated(self):
        pwd = self.gen_result.text()
        if pwd:
            clipboard = QApplication.clipboard()
            clipboard.setText(pwd)
            QMessageBox.information(self, "Скопировано",
                                    "✅ Пароль скопирован в буфер обмена!")

    def lock_app(self):
        reply = QMessageBox.question(
            self, "Блокировка",
            "Заблокировать базу данных?\n\n"
            "Потребуется повторный ввод мастер-пароля.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.storage.lock()
            self.hide()

            dialog = MasterPasswordDialog(parent=self)
            if dialog.exec() and dialog.password:
                if self.storage.unlock(dialog.password):
                    self.show()
                    self.load_passwords()
                else:
                    QMessageBox.critical(None, "Ошибка",
                                         "❌ Неверный пароль!\n\nПриложение будет закрыто.")
                    QApplication.quit()
            else:
                QApplication.quit()