# gui.py - Современный интерфейс с SVG иконками
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QSlider, QCheckBox,
    QMessageBox, QDialog, QDialogButtonBox,
    QApplication, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from storage import StorageManager
from generator import PasswordGenerator
from models import PasswordEntry

# Путь к папке с иконками
ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")


def get_icon(name: str, size: int = 24) -> QIcon:
    """Загрузка SVG иконки с поддержкой цвета темы"""
    path = os.path.join(ICON_DIR, name)
    if os.path.exists(path):
        icon = QIcon(path)
        # Устанавливаем размер по умолчанию
        return icon
    return QIcon()  # Пустая иконка если файл не найден


DARK_THEME = """
QMainWindow {
    background-color: #0d1117;
}
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#nav_panel {
    background-color: #161b22;
    border-radius: 16px;
    border: 1px solid #30363d;
}
QPushButton#nav_button {
    background-color: transparent;
    color: #8b949e;
    border: none;
    padding: 14px 20px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    border-radius: 10px;
}
QPushButton#nav_button:hover {
    background-color: #21262d;
    color: #58a6ff;
}
QPushButton#nav_button:checked {
    background-color: #1f6feb;
    color: white;
}
QPushButton {
    background-color: #238636;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #2ea043;
}
QPushButton:pressed {
    background-color: #1a7f37;
}
QPushButton#secondary {
    background-color: #21262d;
    border: 1px solid #30363d;
}
QPushButton#secondary:hover {
    background-color: #30363d;
}
QPushButton#danger {
    background-color: #da3633;
}
QPushButton#danger:hover {
    background-color: #f85149;
}
QLineEdit, QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 10px 14px;
    color: #c9d1d9;
    font-size: 13px;
}
QLineEdit:focus, QTextEdit:focus {
    border-color: #58a6ff;
    background-color: #161b22;
    border-width: 2px;
}
QCheckBox {
    spacing: 8px;
    color: #c9d1d9;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
}
QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #21262d;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #58a6ff;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QProgressBar {
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
    text-align: center;
    height: 20px;
}
QProgressBar::chunk {
    background-color: #238636;
    border-radius: 3px;
}
QFrame#password_card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
}
QFrame#password_card:hover {
    border-color: #58a6ff;
    background-color: #1c2128;
}
QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #f0f6fc;
}
QLabel#subtitle {
    font-size: 14px;
    color: #8b949e;
}
QScrollArea {
    border: none;
}
QScrollBar:vertical {
    background: #0d1117;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #484f58;
}

/* Отключить outline везде */
* {
    outline: none;
}

*:focus {
    outline: none;
}

QCheckBox:focus, QSlider:focus {
    outline: none;
}
"""


class MasterPasswordDialog(QDialog):
    def __init__(self, is_new: bool = False):
        super().__init__()
        self.is_new = is_new
        self.password = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Мастер-пароль")
        self.setWindowIcon(get_icon("lock.svg"))
        self.setModal(True)
        self.setFixedWidth(450)
        self.setStyleSheet(DARK_THEME)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        if self.is_new:
            title = QLabel("Создание новой базы паролей")
            desc = QLabel("Придумайте надёжный мастер-пароль.\nВосстановление невозможно - запомните его!")
        else:
            title = QLabel("Разблокировка базы данных")
            desc = QLabel("Введите мастер-пароль для доступа к паролям")

        title.setObjectName("title")
        desc.setObjectName("subtitle")
        desc.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addSpacing(10)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Мастер-пароль")
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)

        if self.is_new:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setPlaceholderText("Подтвердите пароль")
            self.confirm_input.setMinimumHeight(40)
            layout.addWidget(self.confirm_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate(self):
        pwd = self.password_input.text()

        if not pwd:
            QMessageBox.warning(self, "Ошибка", "Введите пароль!")
            return

        if self.is_new:
            if len(pwd) < 8:
                QMessageBox.warning(self, "Ошибка",
                                    "Минимальная длина пароля: 8 символов")
                return

            if pwd != self.confirm_input.text():
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
                return

        self.password = pwd
        self.accept()


class AddPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.result = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить пароль")
        self.setWindowIcon(get_icon("add.svg"))
        self.setModal(True)
        self.setFixedSize(550, 620)
        self.setStyleSheet(DARK_THEME)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("Новая запись")
        title.setObjectName("title")
        layout.addWidget(title)

        # Сайт
        site_label = QLabel()
        site_label.setPixmap(get_icon("site.svg").pixmap(QSize(16, 16)))
        site_header = QHBoxLayout()
        site_header.addWidget(site_label)
        site_header.addWidget(QLabel("Сайт:"))
        site_header.addStretch()
        layout.addLayout(site_header)

        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("example.com")
        self.site_input.setMinimumHeight(42)
        layout.addWidget(self.site_input)

        # Логин
        user_label = QLabel()
        user_label.setPixmap(get_icon("user.svg").pixmap(QSize(16, 16)))
        user_header = QHBoxLayout()
        user_header.addWidget(user_label)
        user_header.addWidget(QLabel("Логин:"))
        user_header.addStretch()
        layout.addLayout(user_header)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("user@example.com")
        self.username_input.setMinimumHeight(42)
        layout.addWidget(self.username_input)

        # Пароль
        pwd_label = QLabel()
        pwd_label.setPixmap(get_icon("lock.svg").pixmap(QSize(16, 16)))
        pwd_header = QHBoxLayout()
        pwd_header.addWidget(pwd_label)
        pwd_header.addWidget(QLabel("Пароль:"))
        pwd_header.addStretch()
        layout.addLayout(pwd_header)

        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите или сгенерируйте")
        self.password_input.setMinimumHeight(42)
        self.password_input.textChanged.connect(self.update_strength)
        password_layout.addWidget(self.password_input)

        self.show_password_btn = QPushButton()
        self.show_password_btn.setIcon(get_icon("visibility.svg"))
        self.show_password_btn.setObjectName("secondary")
        self.show_password_btn.setFixedSize(42, 42)
        self.show_password_btn.setIconSize(QSize(20, 20))
        self.show_password_btn.setToolTip("Показать/скрыть пароль")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)

        layout.addLayout(password_layout)

        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        layout.addWidget(self.strength_bar)

        self.strength_label = QLabel("")
        self.strength_label.setObjectName("subtitle")
        layout.addWidget(self.strength_label)

        # Генератор
        gen_frame = QFrame()
        gen_frame.setObjectName("password_card")
        gen_frame.setStyleSheet("""
            QFrame#password_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1f26, stop:1 #161b22);
            }
        """)
        gen_layout = QVBoxLayout()

        gen_header = QHBoxLayout()
        flash_label = QLabel()
        flash_label.setPixmap(get_icon("flash.svg").pixmap(QSize(20, 20)))
        gen_title = QLabel("Генератор паролей")
        gen_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        gen_title.setStyleSheet("color: #58a6ff;")

        gen_header.addWidget(flash_label)
        gen_header.addWidget(gen_title)
        gen_header.addStretch()
        gen_layout.addLayout(gen_header)

        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Длина:"))
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(8, 32)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length_label)
        length_layout.addWidget(self.length_slider)
        self.length_label = QLabel("16")
        self.length_label.setFixedWidth(30)
        length_layout.addWidget(self.length_label)
        gen_layout.addLayout(length_layout)

        options = QHBoxLayout()
        self.upper_cb = QCheckBox("A-Z")
        self.upper_cb.setChecked(True)
        self.digits_cb = QCheckBox("0-9")
        self.digits_cb.setChecked(True)
        self.symbols_cb = QCheckBox("!@#$")
        self.symbols_cb.setChecked(True)

        for cb in [self.upper_cb, self.digits_cb, self.symbols_cb]:
            options.addWidget(cb)

        gen_layout.addLayout(options)

        gen_btn = QPushButton("Сгенерировать")
        gen_btn.setIcon(get_icon("dice.svg"))
        gen_btn.setIconSize(QSize(20, 20))
        gen_btn.setMinimumHeight(44)
        gen_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #238636, stop:1 #2ea043);
                font-size: 14px;
            }
        """)
        gen_btn.clicked.connect(self.generate_password)
        gen_layout.addWidget(gen_btn)

        gen_frame.setLayout(gen_layout)
        layout.addWidget(gen_frame)

        # Кнопки
        buttons = QHBoxLayout()

        save_btn = QPushButton("Сохранить")
        save_btn.setIcon(get_icon("save.svg"))
        save_btn.setIconSize(QSize(20, 20))
        save_btn.setMinimumHeight(48)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #238636, stop:1 #2ea043);
                font-size: 14px;
            }
        """)
        save_btn.clicked.connect(self.save)
        buttons.addWidget(save_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(48)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def update_length_label(self, value):
        self.length_label.setText(str(value))

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setIcon(get_icon("visibility.svg"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setIcon(get_icon("visibility.svg"))

    def generate_password(self):
        pwd = PasswordGenerator.generate(
            length=self.length_slider.value(),
            uppercase=self.upper_cb.isChecked(),
            digits=self.digits_cb.isChecked(),
            symbols=self.symbols_cb.isChecked()
        )
        self.password_input.setText(pwd)

    def update_strength(self):
        pwd = self.password_input.text()
        if not pwd:
            self.strength_bar.setValue(0)
            self.strength_label.setText("")
            return

        strength = PasswordGenerator.estimate_strength(pwd)

        score_map = {
            "Очень слабый": 20,
            "Слабый": 40,
            "Средний": 60,
            "Сильный": 80,
            "Очень сильный": 100
        }
        score = score_map.get(strength, 50)

        self.strength_bar.setValue(score)
        self.strength_label.setText(f"Сила: {strength}")

        if score < 40:
            color = "#da3633"
        elif score < 70:
            color = "#fb8500"
        else:
            color = "#238636"

        self.strength_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)

    def save(self):
        site = self.site_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not site or not username or not password:
            QMessageBox.warning(self, "Ошибка",
                                "Заполните все обязательные поля!")
            return

        self.result = PasswordEntry(
            site=site,
            username=username,
            password=password
        )
        self.accept()


class PasswordCard(QFrame):
    copy_clicked = pyqtSignal(str, str)
    delete_clicked = pyqtSignal(str, str)

    def __init__(self, entry: PasswordEntry):
        super().__init__()
        self.entry = entry
        self.init_ui()

    def init_ui(self):
        self.setObjectName("password_card")
        self.setMinimumHeight(80)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        info_layout = QVBoxLayout()

        # Сайт с иконкой
        site_layout = QHBoxLayout()
        site_icon = QLabel()
        site_icon.setPixmap(get_icon("site.svg").pixmap(QSize(18, 18)))
        site_label = QLabel(self.entry.site)
        site_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        site_label.setStyleSheet("color: #58a6ff;")
        site_layout.addWidget(site_icon)
        site_layout.addWidget(site_label)
        site_layout.addStretch()
        info_layout.addLayout(site_layout)

        # Пользователь
        user_layout = QHBoxLayout()
        user_icon = QLabel()
        user_icon.setPixmap(get_icon("user.svg").pixmap(QSize(14, 14)))
        user_label = QLabel(self.entry.username)
        user_label.setStyleSheet("color: #8b949e; font-size: 13px;")
        user_layout.addWidget(user_icon)
        user_layout.addWidget(user_label)
        user_layout.addStretch()
        info_layout.addLayout(user_layout)

        # Пароль
        pwd_layout = QHBoxLayout()
        lock_icon = QLabel()
        lock_icon.setPixmap(get_icon("lock.svg").pixmap(QSize(14, 14)))
        pwd_label = QLabel("●" * 10)
        pwd_label.setStyleSheet("color: #8b949e; font-size: 13px;")
        pwd_layout.addWidget(lock_icon)
        pwd_layout.addWidget(pwd_label)
        pwd_layout.addStretch()
        info_layout.addLayout(pwd_layout)

        layout.addLayout(info_layout, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        copy_btn = QPushButton("Копировать")
        copy_btn.setIcon(get_icon("copy.svg"))
        copy_btn.setIconSize(QSize(16, 16))
        copy_btn.setObjectName("secondary")
        copy_btn.setFixedWidth(130)
        copy_btn.setMinimumHeight(40)
        copy_btn.clicked.connect(self.on_copy)
        btn_layout.addWidget(copy_btn)

        delete_btn = QPushButton()
        delete_btn.setIcon(get_icon("trash.svg"))
        delete_btn.setIconSize(QSize(18, 18))
        delete_btn.setToolTip("Удалить пароль")
        delete_btn.setObjectName("danger")
        delete_btn.setFixedSize(40, 40)
        delete_btn.clicked.connect(self.on_delete)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def on_copy(self):
        self.copy_clicked.emit(self.entry.password, self.entry.site)

    def on_delete(self):
        self.delete_clicked.emit(self.entry.site, self.entry.username)


class PasswordManagerWindow(QMainWindow):
    def __init__(self, storage: StorageManager):
        super().__init__()
        self.storage = storage
        self.clipboard_timer = None
        self.current_page = 0

        self.init_ui()
        self.load_passwords()

    def init_ui(self):
        self.setWindowTitle("Password Manager")
        self.setWindowIcon(get_icon("lock.svg"))
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet(DARK_THEME)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Левая панель
        nav_panel = QFrame()
        nav_panel.setObjectName("nav_panel")
        nav_panel.setFixedWidth(220)

        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(15, 20, 15, 20)

        logo_icon = QLabel()
        logo_icon.setPixmap(get_icon("lock.svg").pixmap(QSize(48, 48)))
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(logo_icon)

        app_title = QLabel("Password\nManager")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title.setStyleSheet("color: #f0f6fc;")
        nav_layout.addWidget(app_title)

        nav_layout.addSpacing(30)

        self.nav_passwords = QPushButton("Мои пароли")
        self.nav_passwords.setIcon(get_icon("lock.svg"))
        self.nav_passwords.setIconSize(QSize(18, 18))
        self.nav_passwords.setObjectName("nav_button")
        self.nav_passwords.setCheckable(True)
        self.nav_passwords.setChecked(True)
        self.nav_passwords.setMinimumHeight(48)
        self.nav_passwords.clicked.connect(lambda: self.switch_page(0))
        nav_layout.addWidget(self.nav_passwords)

        self.nav_generator = QPushButton("Генератор")
        self.nav_generator.setIcon(get_icon("flash.svg"))
        self.nav_generator.setIconSize(QSize(18, 18))
        self.nav_generator.setObjectName("nav_button")
        self.nav_generator.setCheckable(True)
        self.nav_generator.setMinimumHeight(48)
        self.nav_generator.clicked.connect(lambda: self.switch_page(1))
        nav_layout.addWidget(self.nav_generator)

        nav_layout.addStretch()

        lock_btn = QPushButton("Заблокировать")
        lock_btn.setIcon(get_icon("lock.svg"))
        lock_btn.setIconSize(QSize(18, 18))
        lock_btn.setObjectName("danger")
        lock_btn.setMinimumHeight(48)
        lock_btn.clicked.connect(self.lock_app)
        nav_layout.addWidget(lock_btn)

        nav_panel.setLayout(nav_layout)
        main_layout.addWidget(nav_panel)

        # Правая панель
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(20)

        self.passwords_page = self.create_passwords_page()
        self.generator_page = self.create_generator_page()

        self.content_layout.addWidget(self.passwords_page)
        self.generator_page.hide()

        self.content_area.setLayout(self.content_layout)
        main_layout.addWidget(self.content_area, stretch=1)

        central.setLayout(main_layout)

    def create_passwords_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        header = QHBoxLayout()

        title = QLabel("Мои пароли")
        title.setObjectName("title")
        header.addWidget(title)

        header.addStretch()

        add_btn = QPushButton("Добавить пароль")
        add_btn.setIcon(get_icon("add.svg"))
        add_btn.setIconSize(QSize(18, 18))
        add_btn.setMinimumHeight(44)
        add_btn.clicked.connect(self.add_password)
        header.addWidget(add_btn)

        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по сайту...")
        self.search_input.textChanged.connect(self.filter_passwords)
        layout.addWidget(self.search_input)

        self.password_count_label = QLabel("Всего паролей: 0")
        self.password_count_label.setObjectName("subtitle")
        layout.addWidget(self.password_count_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_container.setLayout(self.cards_layout)

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

        page.setLayout(layout)
        return page

    def create_generator_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("Генератор паролей")
        title.setObjectName("title")
        layout.addWidget(title)

        gen_card = QFrame()
        gen_card.setObjectName("password_card")
        gen_layout = QVBoxLayout()
        gen_layout.setSpacing(15)

        result_label = QLabel("Сгенерированный пароль:")
        gen_layout.addWidget(result_label)

        result_layout = QHBoxLayout()
        self.gen_result = QLineEdit()
        self.gen_result.setReadOnly(True)
        self.gen_result.setPlaceholderText("Нажмите 'Генерировать'")
        self.gen_result.setMinimumHeight(50)
        self.gen_result.setFont(QFont("Courier New", 14))
        result_layout.addWidget(self.gen_result)

        copy_gen_btn = QPushButton()
        copy_gen_btn.setIcon(get_icon("copy.svg"))
        copy_gen_btn.setIconSize(QSize(20, 20))
        copy_gen_btn.setObjectName("secondary")
        copy_gen_btn.setFixedWidth(50)
        copy_gen_btn.clicked.connect(self.copy_generated)
        result_layout.addWidget(copy_gen_btn)

        gen_layout.addLayout(result_layout)

        length_label = QLabel("Длина пароля:")
        gen_layout.addWidget(length_label)

        length_layout = QHBoxLayout()
        self.gen_length = QSlider(Qt.Orientation.Horizontal)
        self.gen_length.setRange(8, 64)
        self.gen_length.setValue(20)
        self.gen_length.valueChanged.connect(self.update_gen_length)
        length_layout.addWidget(self.gen_length)

        self.gen_length_label = QLabel("20")
        self.gen_length_label.setFixedWidth(40)
        self.gen_length_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        length_layout.addWidget(self.gen_length_label)

        gen_layout.addLayout(length_layout)

        options_label = QLabel("Использовать символы:")
        gen_layout.addWidget(options_label)

        self.gen_upper = QCheckBox("Заглавные буквы (A-Z)")
        self.gen_upper.setChecked(True)
        gen_layout.addWidget(self.gen_upper)

        self.gen_lower = QCheckBox("Строчные буквы (a-z)")
        self.gen_lower.setChecked(True)
        gen_layout.addWidget(self.gen_lower)

        self.gen_digits = QCheckBox("Цифры (0-9)")
        self.gen_digits.setChecked(True)
        gen_layout.addWidget(self.gen_digits)

        self.gen_symbols = QCheckBox("Спецсимволы (!@#$%...)")
        self.gen_symbols.setChecked(True)
        gen_layout.addWidget(self.gen_symbols)

        generate_btn = QPushButton("Сгенерировать пароль")
        generate_btn.setIcon(get_icon("dice.svg"))
        generate_btn.setIconSize(QSize(20, 20))
        generate_btn.setMinimumHeight(50)
        generate_btn.clicked.connect(self.generate_password)
        gen_layout.addWidget(generate_btn)

        self.gen_strength = QLabel("")
        self.gen_strength.setObjectName("subtitle")
        gen_layout.addWidget(self.gen_strength)

        gen_card.setLayout(gen_layout)
        layout.addWidget(gen_card)

        layout.addStretch()

        page.setLayout(layout)
        return page

    def switch_page(self, index):
        self.nav_passwords.setChecked(False)
        self.nav_generator.setChecked(False)

        self.passwords_page.hide()
        self.generator_page.hide()

        if index == 0:
            self.passwords_page.show()
            self.nav_passwords.setChecked(True)
            self.load_passwords()
        elif index == 1:
            self.generator_page.show()
            self.nav_generator.setChecked(True)

        self.current_page = index

    def load_passwords(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        passwords = self.storage.get_all_passwords()

        for entry in passwords:
            card = PasswordCard(entry)
            card.copy_clicked.connect(self.copy_password)
            card.delete_clicked.connect(self.delete_password)
            self.cards_layout.addWidget(card)

        self.password_count_label.setText(f"Всего паролей: {len(passwords)}")

        if len(passwords) == 0:
            empty_label = QLabel("Пока нет сохранённых паролей\n\nНажмите 'Добавить пароль' для создания первой записи")
            empty_label.setObjectName("subtitle")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setMinimumHeight(200)
            self.cards_layout.addWidget(empty_label)

    def filter_passwords(self, query):
        query = query.lower()
        for i in range(self.cards_layout.count()):
            widget = self.cards_layout.itemAt(i).widget()
            if isinstance(widget, PasswordCard):
                if query in widget.entry.site.lower() or query in widget.entry.username.lower():
                    widget.show()
                else:
                    widget.hide()

    def add_password(self):
        dialog = AddPasswordDialog()
        if dialog.exec() and dialog.result:
            if self.storage.add_password(dialog.result):
                QMessageBox.information(self, "Успех", "Пароль успешно сохранён!")
                self.load_passwords()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить пароль")

    def copy_password(self, password, site):
        clipboard = QApplication.clipboard()
        clipboard.setText(password)

        QMessageBox.information(self, "Скопировано",
                                f"Пароль для {site} скопирован в буфер обмена!\n\n"
                                "Буфер будет очищен через 30 секунд")

        if self.clipboard_timer:
            self.clipboard_timer.stop()

        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(lambda: self.clear_clipboard(password))
        self.clipboard_timer.setSingleShot(True)
        self.clipboard_timer.start(30000)

    def clear_clipboard(self, original_password):
        clipboard = QApplication.clipboard()
        if clipboard.text() == original_password:
            clipboard.clear()

    def delete_password(self, site, username):
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить пароль для {site} ({username})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.storage.delete_password(site, username):
                QMessageBox.information(self, "Успех", "Пароль удалён!")
                self.load_passwords()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить")

    def generate_password(self):
        pwd = PasswordGenerator.generate(
            length=self.gen_length.value(),
            uppercase=self.gen_upper.isChecked(),
            digits=self.gen_digits.isChecked(),
            symbols=self.gen_symbols.isChecked()
        )

        self.gen_result.setText(pwd)

        strength = PasswordGenerator.estimate_strength(pwd)
        self.gen_strength.setText(f"Сила пароля: {strength}")

    def update_gen_length(self, value):
        self.gen_length_label.setText(str(value))

    def copy_generated(self):
        pwd = self.gen_result.text()
        if pwd:
            clipboard = QApplication.clipboard()
            clipboard.setText(pwd)
            QMessageBox.information(self, "Скопировано",
                                    "Пароль скопирован в буфер обмена!")

    def lock_app(self):
        reply = QMessageBox.question(
            self, "Блокировка",
            "Заблокировать базу данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.storage.close()
            self.hide()

            dialog = MasterPasswordDialog()
            if dialog.exec() and dialog.password and self.storage.unlock(dialog.password):
                self.show()
                self.load_passwords()
            else:
                QApplication.quit()