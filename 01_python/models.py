
from dataclasses import dataclass
from typing import Self

FIELDS = ("date", "product", "category", "quantity", "unit_price")

@dataclass(frozen=True)
class Sale:
    date: str
    product: str
    category: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

    @property
    def month(self) -> str:
        return self.date[:7]

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Self:
        for field in FIELDS:
            value = row.get(field)
            if value is None or not value.strip():
                raise ValueError(f"missing {field}")
        category = row["category"].strip()  # Strip whitespace from category

        return cls(
            date=row["date"],
            product=row["product"],
            category=category,
            quantity=int(row["quantity"]),
            unit_price=float(row["unit_price"]),
        )


if __name__ == "__main__":
    s = Sale.from_row({
        "date": "2026-01-05",
        "product": "Laptop",
        "category": "Electronics",
        "quantity": "2",
        "unit_price": "750.00",
    })

    print(s, s.total, s.month)
