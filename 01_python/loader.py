
import csv
from pathlib import Path

from models import Sale

def load_sales(path: Path) -> tuple[list[Sale], list[str]]:
    sales: list[Sale] = []
    errors: list[str] = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for line_number, row in enumerate(reader, start=2):
            try:
                sale = Sale.from_row(row)                
            except ValueError as e:
                errors.append(f"Line {line_number}: {e}")
            else:
                sales.append(sale)
    return sales, errors


if __name__ == "__main__":
    path = Path(__file__).parent / "data" / "sales.csv"
    sales, errors = load_sales(path)

    print(f"Valid sales: {len(sales)}")
    print(f"Errors: {len(errors)}")

    for error in errors:
        print(error)
