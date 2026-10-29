from pathlib import Path
import json
from dataclasses import asdict

from loader import load_sales
from analysis import grand_total, total_by_category, total_by_month, top_n


def money(amount: float) -> str:
    return f"£{amount:,.2f}"


def main() -> None:
    path = Path(__file__).parent / "data" / "sales.csv"
    sales, errors = load_sales(path)
    
    total_sales = grand_total(sales)
    by_category = total_by_category(sales)
    by_month = total_by_month(sales)
    top_3 = top_n(sales)

        
    print("=== SALES REPORT ===")
    print(f"Valid rows: {len(sales)} | Skipped: {len(errors)}")

    for error in errors:
        print(f"  ! {error}")

    print(f"\nGrand total: {money(total_sales)}")
        
    print("\nBy category:")
    for category, total in by_category.items():
        print(f"  {category:<14}{money(total):>9}")
        
    print("\nBy month:")
    for month, total in by_month.items():
        print(f"  {month:<10}{money(total):>9}")

    print("\nTop 3 sales:")
    for i, sale in enumerate(top_3, start=1):
        print(f"  {i}. {sale.product:<16}{money(sale.total):>9}")
        
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    report = {
        "valid_rows": len(sales),
        "skipped": len(errors),
        "errors": errors,
        "grand_total": total_sales,
        "by_category": {category: total for category, total in by_category.items()},
        "by_month": {month: total for month, total in by_month.items()},
        "top_3": [{**asdict(sale), "total": money(sale.total)} for i, sale in enumerate(top_3, start=1)],        # leave it like this for now — on purpose
    }

    with open(output_dir / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()