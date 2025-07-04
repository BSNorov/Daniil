import sys

# Импорт нужных классов из PyQt6
from PyQt6.QtCore import QSize, Qt  # Размеры, флаги выравнивания
from PyQt6.QtGui import QIcon, QAction, QColor, QPixmap, QPainter  # Иконки, цвета, изображение, рисование
from PyQt6.QtWidgets import (  # Виджеты интерфейса
  QApplication, QMainWindow, QLabel,
  QGraphicsColorizeEffect, QToolBar, QSlider, QPushButton, QColorDialog
)


# Класс холста, где мы будем рисовать
class Canvas(QLabel):
    def __init__(self):
        super().__init__()
        # Создаем изображение размером 800x600 пикселей
        pixmap = QPixmap(800, 600)
        # Заполняем его белым цветом
        pixmap.fill(Qt.GlobalColor.white)
        # Назначаем изображение этому QLabel
        self.setPixmap(pixmap)
        # Устанавливаем фиксированный размер, чтобы QLabel не сжимался
        self.setFixedSize(pixmap.size())

        # Последние координаты мыши (для рисования линии)
        self.last_x, self.last_y = None, None
        # Цвет кисти (по умолчанию черный)
        self.pen_color = QColor("#000000")
        # Толщина линии
        self.pen_size = 4

    # Обработка движения мыши по холсту
    def mouseMoveEvent(self, e):
        # Если это первое движение — просто запоминаем точку
        if self.last_x is None:
            self.last_x = e.position().x()
            self.last_y = e.position().y()
            return

        # Получаем текущее изображение
        canvas = self.pixmap()
        # Создаем рисовальщика
        painter = QPainter(canvas)
        # Включаем сглаживание линий
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Настраиваем кисть
        pen = painter.pen()
        pen.setWidth(self.pen_size)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        # Рисуем линию от предыдущей точки до текущей
        painter.drawLine(int(self.last_x), int(self.last_y), int(e.position().x()), int(e.position().y()))
        # Завершаем рисование
        painter.end()

        # Обновляем изображение на холсте
        self.setPixmap(canvas)

        # Обновляем координаты
        self.last_x = e.position().x()
        self.last_y = e.position().y()

    # Когда отпускаем мышь — сбрасываем координаты
    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Название окна
        self.setWindowTitle("Picasso")
        # Размер окна
        self.setFixedSize(QSize(800, 600))

        # --- Меню ---

        # Создаем меню
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("Файл")

        # Создаем действия с иконками
        new_img_action = QAction(QIcon("icons/new-image.png"), "Создать", self)
        open_action = QAction(QIcon("icons/open-image.png"), "Открыть", self)
        save_action = QAction(QIcon("icons/save-image.png"), "Сохранить", self)

        # Добавляем действия в меню
        file_menu.addAction(new_img_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        # --- Холст ---

        # Создаем объект холста и делаем его центральным виджетом
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        # --- Обработка пунктов меню ---

        # При нажатии выполняются методы
        new_img_action.triggered.connect(self.new_img_text)
        open_action.triggered.connect(self.open_img_text)
        save_action.triggered.connect(self.save_img_text)

        # Создаем панели инструментов
        self.create_toolbars()

    # Метод создания тулбаров
    def create_toolbars(self):
        # --- Панель "Файл" ---
        self.fileToolbar = QToolBar(self)
        self.fileToolbar.setIconSize(QSize(16, 16))
        self.fileToolbar.setObjectName("fileToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.fileToolbar)

        # Кнопка "Создать"
        new_img_button = QPushButton()
        new_img_button.setIcon(QIcon("icons/new-image.png"))
        self.fileToolbar.addWidget(new_img_button)

        # Кнопка "Открыть"
        open_img_button = QPushButton()
        open_img_button.setIcon(QIcon("icons/open-image.png"))
        self.fileToolbar.addWidget(open_img_button)

        # Кнопка "Сохранить"
        save_img_button = QPushButton()
        save_img_button.setIcon(QIcon("icons/save-image.png"))
        self.fileToolbar.addWidget(save_img_button)

        # --- Панель "Слайдер" для толщины линии ---
        self.sliderToolbar = QToolBar(self)
        self.sliderToolbar.setIconSize(QSize(16, 16))
        self.sliderToolbar.setObjectName("sliderToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.sliderToolbar)

        # Иконка перед слайдером
        sizeicon = QLabel()
        sizeicon.setPixmap(QPixmap("icons/border-weight.png").scaled(
            16, 16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.sliderToolbar.addWidget(sizeicon)

        # Слайдер для настройки толщины линии
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(10, 30)
        self.slider.setValue(25)
        self.slider.valueChanged.connect(self.change_pen_size) 
        self.sliderToolbar.addWidget(self.slider)

        # --- Панель "Рисование" ---
        self.drawingToolbar = QToolBar(self)
        self.drawingToolbar.setIconSize(QSize(16, 16))
        self.drawingToolbar.setObjectName("drawingToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.drawingToolbar)

        # Кнопка "Карандаш"
        brush_button = QPushButton()
        brush_button.setIcon(QIcon("icons/paint-brush.png"))
        brush_button.setCheckable(True)
        self.drawingToolbar.addWidget(brush_button)

        # Кнопка "Заливка"
        can_button = QPushButton()
        can_button.setIcon(QIcon("icons/paint-can.png"))
        can_button.setCheckable(True)
        self.drawingToolbar.addWidget(can_button)

        # Кнопка "Ластик"
        eraser_button = QPushButton()
        eraser_button.setIcon(QIcon("icons/eraser.png"))
        eraser_button.setCheckable(True)
        self.drawingToolbar.addWidget(eraser_button)

        # Кнопка "Пипетка"
        picker_button = QPushButton()
        picker_button.setIcon(QIcon("icons/pipette.png"))
        picker_button.setCheckable(True)
        self.drawingToolbar.addWidget(picker_button)
 
        # --- Нижняя панель для выбора цвета ---
        self.bottomToolbar = QToolBar(self)
        self.bottomToolbar.setIconSize(QSize(16, 16))
        self.bottomToolbar.setObjectName("bottomToolbar")
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.bottomToolbar)

        # Кнопка "Цвет" с иконкой и текстом
        self.color_button = QPushButton("Цвет")  # Кнопка с текстом
        self.color_button.setIcon(QIcon("icons/colors.png"))  # Иконка 
        self.color_button.setIconSize(QSize(20, 20))  # Размер иконки
        self.color_button.setMinimumHeight(36)  # Высота кнопки
        self.color_button.setStyleSheet("""  # Простой стиль
            QPushButton {
                padding: 5px 10px;
                font-size: 14px;
            }
        """)
        self.color_button.clicked.connect(self.choose_color)  # Выбор цвета по нажатию
        self.bottomToolbar.addWidget(self.color_button)

    # Добавление кнопки с иконкой в тулбар (без текста)
    def add_toolbar_button(self, toolbar, icon_path):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        toolbar.addWidget(button)

    def change_pen_size(self, value):
        self.canvas.pen_size = value  # Устанавливаем толщину линии для кисти

    # Цветовой эффект на старый label (не используется с Canvas)
    def change_color(self, color_name):
        color_effect = QGraphicsColorizeEffect()
        color_effect.setColor(QColor(color_name))
        self.label.setGraphicsEffect(color_effect)

    # Реакция на пункт меню "Создать"
    def new_img_text(self):
        self.label.setText("НОВОЕ ИЗОБРАЖЕНИЕ")
        self.change_color("green")

    # Реакция на пункт меню "Открыть"
    def open_img_text(self):
        self.label.setText("ОТКРЫТЬ ИЗОБРАЖЕНИЕ")
        self.change_color("blue")

    # Реакция на пункт меню "Сохранить"
    def save_img_text(self):
        self.label.setText("СОХРАНИТЬ ИЗОБРАЖЕНИЕ")
        self.change_color("red")

    # Метод выбора цвета с помощью диалога
    def choose_color(self):
        color = QColorDialog.getColor()  # Открываем диалог выбора цвета
        if color.isValid():  # Если цвет выбран (не отмена)
            self.canvas.pen_color = color  # Применяем к кисти


# Запуск приложения
app = QApplication(sys.argv)  # Создаем приложение
window = MainWindow()         # Создаем главное окно
window.show()                 # Показываем окно пользователю
app.exec()                    # Запускаем цикл событий
