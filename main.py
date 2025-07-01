import sys
import json
import os
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QDialog, QGroupBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QAction, QIcon, QShortcut, QKeySequence


class TextTranslator:
    @staticmethod
    def translate(text, target_lang):
        try:
            source_lang = 'ru' if target_lang == 'en' else 'en'
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            response = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params=params,
                timeout=5
            )
            return response.json()[0][0][0]
        except Exception as e:
            print("Ошибка при переводе:", e)
            return None


class PhraseDatabase:
    def __init__(self):
        self.phrases = {}
        self.load_phrases()

    def load_phrases(self):
        try:
            if os.path.exists('phrases.json'):
                with open('phrases.json', 'r', encoding='utf-8') as f:
                    self.phrases = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.phrases = {}

    def save_phrases(self):
        with open('phrases.json', 'w', encoding='utf-8') as f:
            json.dump(self.phrases, f, ensure_ascii=False, indent=4)

    def get_phrase(self, text):
        return self.phrases.get(text, None)

    def add_phrase(self, text, translation):
        self.phrases[text] = translation

    def import_phrases(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported = json.load(f)
                self.phrases.update(imported)
                return True
        except Exception:
            return False

    def export_phrases(self, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.phrases, f, ensure_ascii=False, indent=4)
                return True
        except Exception:
            return False


class TranslationHistory:
    def __init__(self):
        self.entries = []
        self.load_history()

    def load_history(self):
        try:
            if os.path.exists('history.json'):
                with open('history.json', 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
                    self.entries = self.entries[:50]
        except (FileNotFoundError, json.JSONDecodeError):
            self.entries = []

    def save_history(self):
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=4)

    def add_entry(self, original, translation, source):
        entry = {
            'timestamp': QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm:ss"),
            'original': original,
            'translation': translation,
            'source': source
        }
        self.entries.insert(0, entry)
        self.entries = self.entries[:50]

    def import_history(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported = json.load(f)
                self.entries = imported[:50]
                return True
        except Exception:
            return False

    def export_history(self, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
                return True
        except Exception:
            return False


class HotkeysDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Горячие клавиши")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout()
        group = QGroupBox("Список горячих клавиш")
        vbox = QVBoxLayout()

        hotkeys = [
            ("Ctrl+E", "Перевод на английский"),
            ("Ctrl+R", "Перевод на русский"),
            ("Ctrl+L", "Фокус в поле ввода"),
            ("Ctrl+D", "Очистить поле ввода"),
            ("Ctrl+Shift+C", "Копировать результат"),
            ("Ctrl+Q", "Показать горячие клавиши")
        ]

        for key, desc in hotkeys:
            label = QLabel(f"<b>{key}</b> - {desc}")
            vbox.addWidget(label)

        group.setLayout(vbox)
        layout.addWidget(group)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class TranslationTab(QWidget):
    def __init__(self, translator, database, history):
        super().__init__()
        self.translator = translator
        self.database = database
        self.history = history
        self.setup_ui()
        self.setup_hotkeys()

    def setup_hotkeys(self):
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(lambda: self.translate_text('en'))
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(lambda: self.translate_text('ru'))
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.input_field.setFocus)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.clear_input)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.copy_result)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.show_hotkeys)

    def clear_input(self):
        self.input_field.clear()
        self.input_field.setFocus()

    def copy_result(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_field.toPlainText())
        QMessageBox.information(self, "Скопировано", "Текст скопирован в буфер обмена")

    def show_hotkeys(self):
        dialog = HotkeysDialog(self)
        dialog.exec()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите текст для перевода...")

        btn_layout = QHBoxLayout()
        self.btn_to_english = QPushButton("На английский (Ctrl+E)")
        self.btn_to_russian = QPushButton("На русский (Ctrl+R)")
        self.btn_hotkeys = QPushButton("Горячие клавиши (Ctrl+Q)")
        btn_layout.addWidget(self.btn_to_english)
        btn_layout.addWidget(self.btn_to_russian)
        btn_layout.addWidget(self.btn_hotkeys)

        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setPlaceholderText("Результат перевода (Ctrl+Shift+C - копировать)")

        self.source_label = QLabel("Источник перевода: ")

        layout.addWidget(QLabel("Исходный текст:"))
        layout.addWidget(self.input_field)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self.output_field)
        layout.addWidget(self.source_label)

        self.setLayout(layout)

        self.btn_to_english.clicked.connect(lambda: self.translate_text('en'))
        self.btn_to_russian.clicked.connect(lambda: self.translate_text('ru'))
        self.btn_hotkeys.clicked.connect(self.show_hotkeys)

    def translate_text(self, target_lang):
        text = self.input_field.text().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для перевода")
            return

        translation = self.database.get_phrase(text)
        if translation:
            self.output_field.setPlainText(translation)
            self.source_label.setText("Источник перевода: локальная база")
            self.history.add_entry(text, translation, "local")
            self.history.save_history()
            return

        translation = self.translator.translate(text, target_lang)
        if translation:
            self.output_field.setPlainText(translation)
            self.source_label.setText("Источник перевода: онлайн-сервис")
            self.history.add_entry(text, translation, "online")
            self.history.save_history()

            if QMessageBox.question(
                self, "Сохранение",
                "Сохранить перевод в локальную базу?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
                self.database.add_phrase(text, translation)
                self.database.save_phrases()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось выполнить перевод")
class HistoryTab(QWidget):
    def __init__(self, history):
        super().__init__()
        self.history = history
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["Дата и время", "Оригинал", "Перевод", "Источник"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Очистить историю")
        self.export_btn = QPushButton("Экспорт истории")
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.export_btn)

        layout.addWidget(self.history_table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.clear_btn.clicked.connect(self.clear_history)
        self.export_btn.clicked.connect(self.export_history)

        self.update_history_table()

    def update_history_table(self):
        self.history_table.setRowCount(len(self.history.entries))
        for row, entry in enumerate(self.history.entries):
            timestamp = entry.get('timestamp', '')
            original = entry.get('original', '')
            translation = entry.get('translation', '')
            source = entry.get('source', '')

            self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.history_table.setItem(row, 1, QTableWidgetItem(original))
            self.history_table.setItem(row, 2, QTableWidgetItem(translation))
            item = QTableWidgetItem(source)
            if source == "local":
                item.setForeground(Qt.GlobalColor.darkGreen)
            elif source == "online":
                item.setForeground(Qt.GlobalColor.blue)
            self.history_table.setItem(row, 3, item)

    def clear_history(self):
        if QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите очистить историю переводов?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.history.entries = []
            self.history.save_history()
            self.update_history_table()

    def export_history(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Экспорт истории переводов", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            if self.history.export_history(filename):
                QMessageBox.information(self, "Успех", "История успешно экспортирована")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось экспортировать историю")


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icons/ik.png'))
        self.setWindowTitle("Языковой помощник")
        self.setFixedSize(900, 500)
        self.translator = TextTranslator()
        self.database = PhraseDatabase()
        self.history = TranslationHistory()

        self.setup_interface()
        self.create_menu()

        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI, sans-serif;
                font-size: 13px;
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QLineEdit, QTextEdit {
                background-color: #3b3b3b;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #4682b4;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5a9bd5;
            }
            QPushButton:pressed {
                background-color: #3a6e99;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #444;
                padding: 6px;
                border: none;
            }
            QTableWidget {
                border: 1px solid #444;
                gridline-color: #555;
                background-color: #2b2b2b;
                alternate-background-color: #333;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #444;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #ccc;
            }
            QMenuBar::item:selected {
                background: #3a6e99;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ccc;
            }
            QMenu::item:selected {
                background-color: #3a6e99;
            }
            QTabBar::tab {
                background: #3c3c3c;
                color: #aaa;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #1e90ff;
                color: white;
            }
            QTabWidget::pane {
                border-top: 2px solid #1e90ff;
                top: -1px;
            }
        """)

    def setup_interface(self):
        self.tabs = QTabWidget()

        self.translate_tab = TranslationTab(self.translator, self.database, self.history)
        self.tabs.addTab(self.translate_tab, "Переводчик")

        self.history_tab = HistoryTab(self.history)
        self.tabs.addTab(self.history_tab, "История")

        self.setCentralWidget(self.tabs)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")

        import_phrases_action = QAction("Импорт фраз...", self)
        import_phrases_action.triggered.connect(self.import_phrases)
        file_menu.addAction(import_phrases_action)

        export_phrases_action = QAction("Экспорт фраз...", self)
        export_phrases_action.triggered.connect(self.export_phrases)
        file_menu.addAction(export_phrases_action)

        file_menu.addSeparator()

        import_history_action = QAction("Импорт истории...", self)
        import_history_action.triggered.connect(self.import_history)
        file_menu.addAction(import_history_action)

        export_history_action = QAction("Экспорт истории...", self)
        export_history_action.triggered.connect(self.export_history)
        file_menu.addAction(export_history_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def import_phrases(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Импорт фраз", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            if self.database.import_phrases(filename):
                QMessageBox.information(self, "Успех", "Фразы успешно импортированы")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось импортировать фразы")

    def export_phrases(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Экспорт фраз", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            if self.database.export_phrases(filename):
                QMessageBox.information(self, "Успех", "Фразы успешно экспортированы")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось экспортировать фразы")

    def import_history(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Импорт истории", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            if self.history.import_history(filename):
                self.history_tab.update_history_table()
                QMessageBox.information(self, "Успех", "История успешно импортирована")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось импортировать историю")

    def export_history(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Экспорт истории", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            if self.history.export_history(filename):
                QMessageBox.information(self, "Успех", "История успешно экспортирована")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось экспортировать историю")

    def closeEvent(self, event):
        self.database.save_phrases()
        self.history.save_history()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())
