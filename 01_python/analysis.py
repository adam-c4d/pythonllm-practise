
from models import Sale


def grand_total(sales: list[Sale]) -> float:
    return sum(sale.total for sale in sales)


def total_by_category(sales: list[Sale]) -> dict[str, float]:
    totals: dict[str, float] = {}

    for sale in sales:
        totals[sale.category] = totals.get(sale.category, 0.0) + sale.total

    return totals


def total_by_month(sales: list[Sale]) -> dict[str, float]:
    totals: dict[str, float] = {}

    for sale in sales:
        totals[sale.month] = totals.get(sale.month, 0.0) + sale.total

    return totals


def top_n(sales: list[Sale], n: int = 3) -> list[Sale]:
    return sorted(sales, key=lambda sale: sale.total, reverse=True)[:n]


def filter_category(sales: list[Sale], category: str) -> list[Sale]:
    return [sale for sale in sales if sale.category == category]
