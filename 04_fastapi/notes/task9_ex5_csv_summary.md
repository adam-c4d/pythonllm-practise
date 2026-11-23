# Task 9, Exercise 5: `POST /summary`: upload a CSV, get statistics back (worked example)

Continue in `04_fastapi/task9/`, in `main.py` and `schemas.py` (finished files: [examples/task9/ex5/](../examples/task9/ex5/)). The outputs below are real (run on 2026-11-23).

**The idea:** so far every request was JSON. Now the client **uploads a file**, the server reads it with pandas, and it returns a short summary: rows, columns, gaps, averages. This is the first endpoint of the **capstone** ("Ask Your Data" API), and the same pandas you used in Tasks 3–4, now behind a URL.

- **Laravel analogy:** `$request->file('file')` with the rule `'file' => 'required|file|mimes:csv'`, then reading the file in the controller.

## Step 1: a reply model, in `schemas.py`

```python
class Summary(BaseModel):
    filename: str
    rows: int
    columns: list[str]
    missing_values: dict[str, int] = Field(description="Only columns with gaps")
    numeric_means: dict[str, float]
```
- **`dict[str, int]`**: a JSON object whose keys are strings (column names) and whose values are whole numbers, for example `{"cut": 1}`.

## Step 2: the route, in `main.py`

Add `UploadFile` to the FastAPI import and `Summary` to the schemas import:
```python
from fastapi import Body, Depends, FastAPI, HTTPException, UploadFile

from schemas import BatchPrediction, DiamondIn, Prediction, Summary
```
Under `MODEL_FILE`, add one constant:
```python
CSV_ERRORS = (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError)
```
And the route at the bottom:
```python
@app.post("/summary")
def summary(file: UploadFile) -> Summary:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    try:
        df = pd.read_csv(file.file)
    except CSV_ERRORS as error:
        raise HTTPException(status_code=400, detail=f"Bad CSV: {error}") from error
    missing = df.isna().sum()
    return Summary(
        filename=filename,
        rows=len(df),
        columns=df.columns.tolist(),
        missing_values=missing[missing > 0].to_dict(),
        numeric_means=df.mean(numeric_only=True).dropna().round(2).to_dict(),
    )
```

## Step 3: try it

**In `/docs`:** open `POST /summary` → **Try it out**. Instead of a JSON box there is a **Choose File** button. Pick `03_ml/data/diamonds.csv` → **Execute**.

**With `curl.exe`**, from inside `04_fastapi/task9/` (file uploads have no quote problem in PowerShell):
```powershell
curl.exe -s -F "file=@../../03_ml/data/diamonds.csv" http://127.0.0.1:8001/summary
```
```
{"filename":"diamonds.csv","rows":53940,"columns":["carat","cut","color","clarity","depth","table","price","x","y","z"],"missing_values":{},"numeric_means":{"carat":0.8,"depth":61.75,"table":57.46,"price":3932.8,"x":5.73,"y":5.73,"z":3.54}}
```
53,940 rows, 10 columns, no gaps, average price $3,932.80: the same as Task 6 Ex 1 (which printed it rounded, `$3,933`).

A small file with a gap, `small.csv`:
```
carat,cut,price
0.5,Ideal,1800
1.0,,4600
```
```
200 OK
{
  "filename": "small.csv",
  "rows": 2,
  "columns": [
    "carat",
    "cut",
    "price"
  ],
  "missing_values": {
    "cut": 1
  },
  "numeric_means": {
    "carat": 0.75,
    "price": 3200.0
  }
}
```
Now the bad files. A text file, `notes.txt`:
```
400 Bad Request
{
  "detail": "Please upload a .csv file"
}
```
An empty `empty.csv`:
```
400 Bad Request
{
  "detail": "Bad CSV: No columns to parse from file"
}
```
A CSV saved in an old Windows encoding (Latin-1) with `café` in it:
```
400 Bad Request
{
  "detail": "Bad CSV: 'utf-8' codec can't decode byte 0xe9 in position 3: unexpected end of data"
}
```

## Why each part works

- **`file: UploadFile`**: a parameter of type `UploadFile` means "a file in a form upload" (`multipart/form-data`), not JSON. It needs the `python-multipart` package, which came with `fastapi[standard]`. The parameter name `file` is the form field name: that's why curl says `-F "file=@..."`.
- **`file.filename`** is the name on the client's computer. It can be `None`, so `or ""` gives an empty string instead. **`.lower().endswith(".csv")`** also accepts `DATA.CSV`.
- **400 Bad Request, not 422:** 422 is what FastAPI uses for "the request didn't match the schema". 400 is the general "your request is wrong" code, a good fit for "right shape, but not a usable CSV". Laravel would give 422 for both; either is defensible, as long as you're consistent.
- **`file.file`** is the uploaded data as a normal Python file object. `pd.read_csv` reads from a file object as happily as from a path, so nothing is saved to disk.
- **`CSV_ERRORS`, a tuple of exceptions:** `except (A, B, C)` catches any of them. They are the 3 ways a bad upload fails in `read_csv`: broken structure (`ParserError`), nothing in it (`EmptyDataError`), and not UTF-8 text (`UnicodeDecodeError`). Anything else is a real bug and should still be a 500.
- **`raise ... from error`** keeps the original exception attached, so the server log shows both ("During handling of the above exception..." becomes "The above exception was the direct cause..."). Use it whenever you raise a new exception inside an `except` block.
- **`df.isna().sum()`** counts gaps per column (Task 3). **`missing[missing > 0]`** keeps only the columns that have gaps (a boolean mask), and **`.to_dict()`** turns the Series into `{"cut": 1}`.
- **`df.mean(numeric_only=True)`** averages only the number columns and skips text columns like `cut`. **`.dropna()`** drops a number column that is completely empty (its mean would be `NaN`, which JSON can't hold). **`.round(2)`** keeps the reply readable.
- **`df.columns.tolist()`**: pandas `Index` → plain Python list, which JSON can hold.
- **Plain `def` again.** `pd.read_csv` is ordinary blocking code, and FastAPI runs plain `def` routes in a thread pool, so one big upload doesn't freeze other requests.

## A limitation to know about

A CSV that uses `;` between values (common in European Excel exports) is **not** an error for pandas. It reads each line as **one** column:
```
200 OK → "columns": ["a;b"], "numeric_means": {}
```
The reply is "valid" but useless. Spotting the separator (`pd.read_csv(..., sep=None, engine="python")` can guess it) is a good extra for the capstone.

## Recap
- `file: UploadFile` receives a form upload. `file.filename` is its name, and `file.file` is its data for `pd.read_csv`.
- Check the extension, then catch the 3 CSV read errors and turn them into a 400 with a clear message.
- `isna().sum()`, `mean(numeric_only=True)` and `.to_dict()` turn pandas results into JSON.
- This is the capstone's `/summary`. In December you'll add charts and the `/ask` endpoint on top.

📚 **Learn more:** [FastAPI: Request Files (`UploadFile`)](https://fastapi.tiangolo.com/tutorial/request-files/) · [`pandas.read_csv`](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) · [`DataFrame.mean`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.mean.html) · [pandas errors](https://pandas.pydata.org/docs/reference/api/pandas.errors.ParserError.html) · [MDN: 400 Bad Request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/400)
