from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QHeaderView, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QSlider,
    QTableWidget, QTableWidgetItem
)

class PrimaryButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet(
            "QPushButton {background-color: #3949ab; color: white; padding: 6px 16px; border-radius: 4px;}"
            "QPushButton:hover {background-color: #5c6bc0;}"
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class LoginField(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Логин")
        self.setFixedWidth(300)

    def is_valid(self):
        return len(self.text().strip()) >= 3


class SearchField(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Поиск по названию или бренду")
        self.setClearButtonEnabled(True)

    def query(self):
        return self.text().strip().lower()


class HeaderLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.setFont(font)
        self.setStyleSheet("color: #3949ab;")


class CategoryCombo(QComboBox):
    ALL = "Все категории"

    def __init__(self, categories):
        super().__init__()
        self.addItem(self.ALL)
        self.addItems(categories)

    def selected(self):
        return None if self.currentIndex() == 0 else self.currentText()


class PriceSlider(QSlider):
    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        self.setRange(10, 120)
        self.setValue(120)
        self.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.setTickInterval(10)

    def max_price(self):
        return self.value() * 1000


class HideEqualCheckBox(QCheckBox):
    def __init__(self):
        super().__init__("Скрыть одинаковые")


class StatusBar(QLabel):
    def __init__(self):
        super().__init__("")

    def show_message(self, message, error=False):
        self.setText(message)
        self.setStyleSheet("color: #c62828;" if error else "color: #555555;")


class ProductList(QListWidget):
    def __init__(self):
        super().__init__()
        self.products = []

    def fill(self, products, picked):
        self.clear()
        self.products = list(products)
        for p in self.products:
            self.addItem(QListWidgetItem(f"{p.brand} {p.name}   {p.price} ₽   ★ {p.rating}"))
        self.mark(picked)

    def mark(self, picked):
        for i, p in enumerate(self.products):
            color = QBrush(QColor("#c5cae9")) if p in picked else QBrush()
            self.item(i).setBackground(color)

    def product_of(self, item):
        return self.products[self.row(item)]


class SlotLabel(QLabel):
    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        self.setWordWrap(True)
        self.setMinimumHeight(50)
        self.setStyleSheet("border: 1px solid #9e9e9e; border-radius: 6px; padding: 6px;")
        self.set_product(None)

    def set_product(self, product):
        if product is None:
            self.setText(f"{self.letter}: не выбран")
        else:
            self.setText(f"{self.letter}: {product.describe()}")


class CompareTable(QTableWidget):
    def __init__(self):
        super().__init__(0, 4)
        self.setHorizontalHeaderLabels(["Характеристика", "Товар A", "Товар B", "Лучше"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def fill(self, rows, hide_equal=False):
        shown = [r for r in sorted(rows) if not (hide_equal and r.winner == 0)]
        self.setRowCount(len(shown))
        for i, r in enumerate(shown):
            self.setItem(i, 0, QTableWidgetItem(r.spec_name))
            self.setItem(i, 1, self._cell(f"{r.value_a} {r.unit}", r.winner == 1))
            self.setItem(i, 2, self._cell(f"{r.value_b} {r.unit}", r.winner == 2))
            self.setItem(i, 3, QTableWidgetItem(r.mark()))

    @staticmethod
    def _cell(text, is_winner):
        item = QTableWidgetItem(text)
        if is_winner:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            item.setForeground(QColor("#2e7d32"))
        return item