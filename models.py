import itertools
import json
from abc import ABC, abstractmethod
from datetime import datetime
from functools import total_ordering
from pathlib import Path

FMT = "%d.%m.%Y %H:%M:%S"
DB_PATH = Path(__file__).with_name("products.json")


class Entity(ABC):
    _counter = itertools.count(1)

    def __init__(self):
        self._id = next(Entity._counter)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value <= 0:
            raise ValueError("id должен быть положительным")
        self._id = value

    @abstractmethod
    def describe(self):
        pass


@total_ordering
class Spec(Entity):
    def __init__(self, name, value, unit="", higher_is_better=True):
        super().__init__()
        self.name = name
        self.value = value
        self.unit = unit
        self.higher_is_better = higher_is_better

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value.strip():
            raise ValueError("Название характеристики пустое")
        self._name = value.strip()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Значение должно быть числом")
        self._value = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def higher_is_better(self):
        return self._higher_is_better

    @higher_is_better.setter
    def higher_is_better(self, value):
        self._higher_is_better = bool(value)

    def score(self):
        return self._value if self._higher_is_better else -self._value

    def describe(self):
        return f"{self._name}: {self._value} {self._unit}".strip()

    def __eq__(self, other):
        return isinstance(other, Spec) and self._name == other._name and self._value == other._value

    def __lt__(self, other):
        return self.score() < other.score()

    def __hash__(self):
        return hash((self._name, self._value))

    def __repr__(self):
        return f"Spec({self._name!r}, {self._value!r}, {self._unit!r})"

    def __str__(self):
        return self.describe()


@total_ordering
class Product(Entity):
    def __init__(self, name, brand, category, price, rating, specs):
        super().__init__()
        self.name = name
        self.brand = brand
        self.category = category
        self.price = price
        self.rating = rating
        self.specs = specs

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value.strip():
            raise ValueError("Название товара пустое")
        self._name = value.strip()

    @property
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, value):
        self._brand = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value <= 0:
            raise ValueError("Цена должна быть больше нуля")
        self._price = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if not 0 <= value <= 5:
            raise ValueError("Рейтинг от 0 до 5")
        self._rating = value

    @property
    def specs(self):
        return self._specs

    @specs.setter
    def specs(self, value):
        self._specs = list(value)

    def all_specs(self):
        extra = [
            Spec("Цена", self._price, "₽", False),
            Spec("Рейтинг", self._rating, "", True),
        ]
        return self._specs + extra

    def find_spec(self, name):
        for spec in self.all_specs():
            if spec.name == name:
                return spec
        return None

    def describe(self):
        return f"{self._brand} {self._name} — {self._price} ₽"

    def __eq__(self, other):
        return isinstance(other, Product) and self._name == other._name and self._brand == other._brand

    def __lt__(self, other):
        return self._price < other._price

    def __hash__(self):
        return hash((self._name, self._brand))

    def __repr__(self):
        return f"Product({self._name!r}, {self._brand!r}, {self._price!r})"

    def __str__(self):
        return self.describe()


@total_ordering
class SpecComparison(Entity):
    def __init__(self, spec_name, unit, value_a, value_b, winner):
        super().__init__()
        self.spec_name = spec_name
        self.unit = unit
        self.value_a = value_a
        self.value_b = value_b
        self.winner = winner

    @property
    def spec_name(self):
        return self._spec_name

    @spec_name.setter
    def spec_name(self, value):
        self._spec_name = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def value_a(self):
        return self._value_a

    @value_a.setter
    def value_a(self, value):
        self._value_a = value

    @property
    def value_b(self):
        return self._value_b

    @value_b.setter
    def value_b(self, value):
        self._value_b = value

    @property
    def winner(self):
        return self._winner

    @winner.setter
    def winner(self, value):
        if value not in (0, 1, 2):
            raise ValueError("winner: 0 - ничья, 1 - A, 2 - B")
        self._winner = value

    def mark(self):
        return ("=", "A", "B")[self._winner]

    def describe(self):
        return f"{self._spec_name}: {self._value_a} / {self._value_b} -> {self.mark()}"

    def __eq__(self, other):
        return (isinstance(other, SpecComparison)
                and self._spec_name == other._spec_name
                and self._value_a == other._value_a
                and self._value_b == other._value_b)

    def __lt__(self, other):
        return self._spec_name < other._spec_name

    def __hash__(self):
        return hash((self._spec_name, self._value_a, self._value_b))

    def __repr__(self):
        return f"SpecComparison({self._spec_name!r}, {self._value_a!r}, {self._value_b!r})"

    def __str__(self):
        return self.describe()


class Registry(Entity):
    """Кастомный класс маппинга вместо запрещенного словаря (dict)."""
    def __init__(self):
        super().__init__()
        self._keys = []
        self._values = []

    def put(self, key, value):
        if key in self._keys:
            self._values[self._keys.index(key)] = value
        else:
            self._keys.append(key)
            self._values.append(value)

    def get(self, key, default=None):
        if key in self._keys:
            return self._values[self._keys.index(key)]
        return default

    def remove(self, key):
        if key in self._keys:
            index = self._keys.index(key)
            self._keys.pop(index)
            self._values.pop(index)

    def keys(self):
        return list(self._keys)

    def values(self):
        return list(self._values)

    @staticmethod
    def from_pairs(pairs):
        reg = Registry()
        for key, value in pairs:
            reg.put(key, value)
        return reg

    def describe(self):
        return f"Registry, записей: {len(self._keys)}"

    def __len__(self):
        return len(self._keys)

    def __contains__(self, key):
        return key in self._keys

    def __eq__(self, other):
        return isinstance(other, Registry) and self._keys == other._keys and self._values == other._values

    def __lt__(self, other):
        return len(self) < len(other)

    def __repr__(self):
        return f"Registry(keys={self._keys!r})"

    def __str__(self):
        return self.describe()


class Session(Entity):
    def __init__(self, login):
        super().__init__()
        self.login = login
        self._time_in = datetime.now()
        self._time_out = None

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        if len(value.strip()) < 3:
            raise ValueError("Логин минимум 3 символа")
        self._login = value.strip()

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        self._time_out = value

    def close(self):
        self._time_out = datetime.now()

    def describe(self):
        return f"{self._login}: {self._time_in.strftime(FMT)}"

    def __eq__(self, other):
        return isinstance(other, Session) and self._login == other._login and self._time_in == other._time_in

    def __lt__(self, other):
        return self._time_in < other._time_in

    def __hash__(self):
        return hash((self._login, self._time_in))

    def __repr__(self):
        return f"Session({self._login!r}, {self._time_in!r})"

    def __str__(self):
        return self.describe()


class Catalog(Entity):
    def __init__(self):
        super().__init__()
        self._products = []

    @property
    def products(self):
        return self._products

    @products.setter
    def products(self, value):
        self._products = list(value)

    def add(self, product):
        if product not in self._products:
            self._products.append(product)

    def categories(self):
        names = []
        for p in self._products:
            if p.category not in names:
                names.append(p.category)
        return names

    def filter(self, text="", category=None, max_price=None):
        result = []
        for p in self._products:
            if text and text not in p.name.lower() and text not in p.brand.lower():
                continue
            if category is not None and p.category != category:
                continue
            if max_price is not None and p.price > max_price:
                continue
            result.append(p)
        return result

    def describe(self):
        return f"Каталог: {len(self._products)} товаров"

    def __len__(self):
        return len(self._products)

    def __eq__(self, other):
        return isinstance(other, Catalog) and self._products == other._products

    def __lt__(self, other):
        return len(self) < len(other)

    def __repr__(self):
        return f"Catalog({len(self._products)} products)"

    def __str__(self):
        return self.describe()

    @staticmethod
    def load(path=DB_PATH):
        with open(path, encoding="utf-8") as f:
            data = json.load(f, object_pairs_hook=Registry.from_pairs)

        schemas = Registry()
        for category in data.get("categories"):
            schemas.put(category.get("name"), category.get("specs"))

        catalog = Catalog()
        for item in data.get("products"):
            schema = schemas.get(item.get("category"))
            if schema is None:
                raise ValueError(f"Неизвестная категория: {item.get('category')}")
            specs = [
                Spec(rule.get("name"), value, rule.get("unit", ""), rule.get("higher_is_better", True))
                for rule, value in zip(schema, item.get("values"))
            ]
            catalog.add(Product(
                item.get("name"), item.get("brand"), item.get("category"),
                item.get("price"), item.get("rating"), specs,
            ))
        return catalog


class Comparator:
    @staticmethod
    def compare(a, b):
        rows = []
        for spec_a in a.all_specs():
            spec_b = b.find_spec(spec_a.name)
            if spec_b is None:
                continue
            if spec_a == spec_b:
                winner = 0
            elif spec_a > spec_b:
                winner = 1
            else:
                winner = 2
            rows.append(SpecComparison(spec_a.name, spec_a.unit, spec_a.value, spec_b.value, winner))
        return rows

    @staticmethod
    def count_wins(rows):
        wins_a = len([r for r in rows if r.winner == 1])
        wins_b = len([r for r in rows if r.winner == 2])
        return wins_a, wins_b


class ReportWriter:
    @staticmethod
    def save(session, path="report.txt"):
        time_out = session.time_out or datetime.now()
        table = [
            ["login", "time_in", "time_out"],
            [session.login, session.time_in.strftime(FMT), time_out.strftime(FMT)],
        ]
        widths = [max(len(row[i]) for row in table) for i in range(3)]

        def line(row):
            cells = [row[i].ljust(widths[i]) for i in range(3)]
            return "| " + " | ".join(cells) + " |"

        border = "+" + "-" * (len(line(table[0])) - 2) + "+"
        separator = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
        with open(path, "w", encoding="utf-8") as f:
            f.write(border + "\n")
            f.write(line(table[0]) + "\n")
            f.write(separator + "\n")
            f.write(line(table[1]) + "\n")
            f.write(border + "\n")