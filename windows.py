from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from models import Catalog, Comparator, ReportWriter, Session
from widgets import (
    CategoryCombo, CompareTable, HeaderLabel, HideEqualCheckBox,
    LoginField, PrimaryButton, PriceSlider, ProductList,
    SearchField, SlotLabel, StatusBar
)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.resize(400, 280)
        self.main_window = None

        self.field = LoginField()
        self.button = PrimaryButton("Войти")
        self.status = StatusBar()
        self.field.returnPressed.connect(self.do_login)
        self.button.clicked.connect(self.do_login)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        for widget in (HeaderLabel("Сравнение товаров"), self.field, self.button, self.status):
            layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def do_login(self):
        if not self.field.is_valid():
            self.status.show_message("Логин минимум 3 символа", error=True)
            return
        session = Session(self.field.text())
        self.main_window = MainWindow(session)
        self.main_window.show()
        self.close()


class MainWindow(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.catalog = Catalog.load()
        self.picked = []
        self.rows = []

        self.setWindowTitle("Сравнение товаров")
        self.resize(1100, 720)
        self.build()
        self.refresh_list()

    def build(self):
        self.search = SearchField()
        self.category = CategoryCombo(self.catalog.categories())
        self.price = PriceSlider()
        self.price_label = QLabel()
        self.product_list = ProductList()
        self.slot_a = SlotLabel("A")
        self.slot_b = SlotLabel("B")
        self.compare_btn = PrimaryButton("Сравнить")
        self.reset_btn = PrimaryButton("Сбросить")
        self.hide_equal = HideEqualCheckBox()
        self.verdict = QLabel("")
        self.table = CompareTable()
        self.status = StatusBar()

        self.search.textChanged.connect(self.refresh_list)
        self.category.currentIndexChanged.connect(self.refresh_list)
        self.price.valueChanged.connect(self.refresh_list)
        self.product_list.itemClicked.connect(self.on_pick)
        self.compare_btn.clicked.connect(self.compare)
        self.reset_btn.clicked.connect(self.reset)
        self.hide_equal.stateChanged.connect(self.show_table)

        top = QHBoxLayout()
        top.addWidget(HeaderLabel("Сравнение товаров"))
        top.addStretch()
        top.addWidget(QLabel(f"Пользователь: {self.session.login}"))

        left = QVBoxLayout()
        left.setAlignment(Qt.AlignmentFlag.AlignTop)
        left.addWidget(self.search)
        left.addWidget(self.category)
        left.addWidget(self.price_label)
        left.addWidget(self.price)
        left.addWidget(self.product_list)

        slots = QHBoxLayout()
        slots.addWidget(self.slot_a)
        slots.addWidget(self.slot_b)

        buttons = QHBoxLayout()
        buttons.addWidget(self.compare_btn)
        buttons.addWidget(self.reset_btn)
        buttons.addWidget(self.hide_equal)
        buttons.addStretch()

        right = QVBoxLayout()
        right.addLayout(slots)
        right.addLayout(buttons)
        right.addWidget(self.verdict)
        right.addWidget(self.table)

        body = QHBoxLayout()
        body.addLayout(left, 1)
        body.addLayout(right, 2)

        main = QVBoxLayout(self)
        main.addLayout(top)
        main.addLayout(body)
        main.addWidget(self.status)

    def refresh_list(self):
        max_price = self.price.max_price()
        self.price_label.setText(f"Максимальная цена: {max_price} ₽")
        found = self.catalog.filter(self.search.query(), self.category.selected(), max_price)
        self.product_list.fill(sorted(found), self.picked)
        self.status.show_message(f"Найдено товаров: {len(found)}")

    def on_pick(self, item):
        product = self.product_list.product_of(item)
        if product in self.picked:
            self.picked.remove(product)
        else:
            if len(self.picked) == 2:
                self.picked.pop(0)
            self.picked.append(product)
        self.update_slots()

    def update_slots(self):
        self.slot_a.set_product(self.picked[0] if len(self.picked) > 0 else None)
        self.slot_b.set_product(self.picked[1] if len(self.picked) > 1 else None)
        self.product_list.mark(self.picked)

    def compare(self):
        if len(self.picked) < 2:
            self.status.show_message("Выберите два товара", error=True)
            return
        a, b = self.picked
        if a.category != b.category:
            self.status.show_message("Сравнивать можно только товары одной категории", error=True)
            return
        self.rows = Comparator.compare(a, b)
        wins_a, wins_b = Comparator.count_wins(self.rows)
        self.verdict.setText(f"A лучше в {wins_a}, B лучше в {wins_b}, из {len(self.rows)} характеристик")
        self.status.show_message("Сравнение готово")
        self.show_table()

    def show_table(self):
        self.table.fill(self.rows, self.hide_equal.isChecked())

    def reset(self):
        self.picked = []
        self.rows = []
        self.verdict.setText("")
        self.table.fill([])
        self.update_slots()

    def closeEvent(self, event):
        self.session.close()
        ReportWriter.save(self.session)
        event.accept()