from pathlib import Path
import pandas as pd

CSV_PATH = Path(__file__).parent.parent/  "01_python"/"data"/"sales.csv"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["category"] = df["category"].str.strip().replace("", None)
    df = df.dropna(subset=["quantity", "category"])
    df["quantity"] = df["quantity"].astype(int)
    df["total"] = df["quantity"] * df["unit_price"]
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

    print(f"Grand Total: £{df['total'].sum():,.2f}")
    print(f"\nBy Category:", df.groupby('category')['total'].sum().to_string(float_format='£{:,.2f}'.format), sep="\n")
    print(f"\nBy Month:", df.groupby('month')['total'].sum().to_string(float_format='£{:,.2f}'.format), sep="\n")
    print(f"\nTop 3 Sales:", df.nlargest(3, 'total')[['product', 'total']].to_string(index=False), sep="\n")
    
if __name__ == "__main__":
    main()