"""Turn any DataFrame into a small, JSON-friendly summary."""

import pandas as pd


def summarise(df: pd.DataFrame) -> dict:
    """Rows, columns, gaps, and simple stats for number and text columns."""
    numbers = df.select_dtypes("number").dropna(axis=1, how="all")
    texts = df.select_dtypes(exclude="number").dropna(axis=1, how="all")
    missing = df.isna().sum()
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "missing": {col: int(count) for col, count in missing.items() if count > 0},
        "numeric": {
            col: {
                "mean": round(float(numbers[col].mean()), 2),
                "min": numbers[col].min().item(),
                "max": numbers[col].max().item(),
            }
            for col in numbers.columns
        },
        "text": {
            col: {"unique": int(texts[col].nunique()), "top": str(texts[col].mode()[0])}
            for col in texts.columns
        },
    }
