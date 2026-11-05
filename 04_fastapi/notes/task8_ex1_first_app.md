# Task 8, Exercise 1: Your first API (worked example)

**Make the folder** `04_fastapi/task8/` and a new file `main.py` in it. You type the code there; the finished file is also in [examples/task8/ex1/](../examples/task8/ex1/). The outputs below are real (run on 2026-11-05).

**The idea:** a FastAPI app is one Python object, `app`. Each route is a normal function with a **decorator** (`@app.get("/")`) on top that says "call this function for GET requests to `/`". Whatever the function returns becomes the JSON reply. It's Laravel's `Route::get('/', fn () => [...])`, with the route written next to the function.

**How these notes show requests:** a request is an ```` ```http ```` block (method and URL, then headers and a JSON body if there are any). You can send it from the browser (GET only), from `/docs` (any request, see Step 4), or with `curl.exe`. The reply below it shows the status code, then the JSON body, indented the way `/docs` shows it.

## Step 1: The smallest app

```python
from fastapi import FastAPI

app = FastAPI(title="Diamond Shop")


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to Diamond Shop"}
```
Nothing runs yet: the file only defines the app. Step 2 starts it.

- **`app = FastAPI(title=...)`** creates the application. The title appears in `/docs`. Laravel creates its app for you in `bootstrap/app.php`; in FastAPI you create it yourself, in one line.
- **`@app.get("/")`** is a **decorator**: the line above a function that registers it. Here it means "GET `/` → call `home()`". Other methods have their own decorators: `@app.post`, `@app.patch`, `@app.delete` (Exercises 3 and 4).
- **The function returns a dict, and FastAPI turns it into JSON**, like a Laravel route that returns an array.
- **`-> dict[str, str]`** is the return type: a dict with string keys and string values. FastAPI uses it to check the reply and to describe it in `/docs`. Write return types on every route.
- **Plain `def`, not `async def`:** both work. FastAPI runs plain `def` routes in a background thread, so slow work (like pandas or a model in Task 9) doesn't block other requests. Use plain `def` until a library tells you to `await` something.

## Step 2: Start the server

```powershell
cd 04_fastapi/task8
fastapi dev main.py --port 8001
```
```
 ⚡️ Starting FastAPI in development mode
 
 🐍 Using import string: main:app
 
 🌐 Server started at http://127.0.0.1:8001
    Documentation at http://127.0.0.1:8001/docs
 
  Logs:
 
INFO:     Will watch for changes in these directories: ['C:\\Users\\phpde\\OneDrive\\Desktop\\pythonllm-practise\\04_fastapi\\examples\\task8\\ex1']
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [9596] using WatchFiles
INFO:     Started server process [20748]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
Your terminal shows this with colours and a slightly different layout, and the folder path is your `task8` folder.

- **Run it in a `(dsllm)` terminal**, from inside `task8/`. In another terminal, `fastapi` may not exist, or may be a different Python's copy.
- **`fastapi dev` ≈ `php artisan serve`:** a development server that **reloads** when you save a file ("Will watch for changes"). For production, `fastapi run main.py` does the same without reloading and listens on all network cards.
- **`--port 8001` every time.** Your Laravel `php artisan serve` already uses 8000. Careful: on Windows, a second server on a busy port can start **without any error** (I tried two FastAPI servers on 8001: both said "Application startup complete"). Then you can't tell which server answers your requests.
- **"Using import string: main:app"** means "the object `app` in the file `main.py`". If you name the file or the object differently, this is where it goes wrong.
- **uvicorn** is the actual web server (≈ php-fpm). `fastapi dev` starts it for you. Every request is logged here: `"GET / HTTP/1.1" 200 OK`.
- **Stop it with Ctrl+C.** Leave it running while you work; open a **second terminal** for other commands.

## Step 3: Call it

Open http://127.0.0.1:8001/ in the browser, or run this in a second terminal:
```powershell
curl.exe -s -i http://127.0.0.1:8001/
```
```
HTTP/1.1 200 OK
date: Thu, 05 Nov 2026 11:55:42 GMT
server: uvicorn
content-length: 37
content-type: application/json

{"message":"Welcome to Diamond Shop"}
```
- **Type `curl.exe`, not `curl`.** In Windows PowerShell, `curl` is a nickname for `Invoke-WebRequest`, which prints something completely different. `-s` hides the progress bar and `-i` shows the status line and headers.
- **`content-type: application/json`:** FastAPI set it, because the function returned a dict. Like Laravel, you never call `json_encode` yourself.
- **A URL with no route** gets `404` and `{"detail":"Not Found"}`. FastAPI puts every error message under `"detail"`. You'll see it a lot.
- **To send JSON bodies, use `/docs`** (next step). Windows PowerShell 5.1 removes the `"` quotes inside arguments it passes to `curl.exe`, so `curl.exe --json '{"a": 1}'` doesn't work there. In `/docs`, it just works.

## Step 4: The free documentation: `/docs` and `/openapi.json`

```http
GET http://127.0.0.1:8001/openapi.json
```
```
{"openapi":"3.1.0","info":{"title":"Diamond Shop","version":"0.1.0"},"paths":{"/":{"get":{"summary":"Home","operationId":"home__get","responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{"additionalProperties":{"type":"string"},"type":"object","title":"Response Home  Get"}}}}}}}}}
```
- **`/openapi.json` is a machine-readable description of your API** (the OpenAPI 3.1 standard). FastAPI builds it from your code: the path, the method, and `dict[str, str]` became `"additionalProperties": {"type": "string"}`. The function name `home` became the summary "Home".
- **Now open http://127.0.0.1:8001/docs.** It's an interactive page (Swagger UI) built from that JSON. At the top: **Diamond Shop 0.1.0 OAS 3.1**. Below it, a **default** section with a blue **GET /** bar, labelled **Home**. Click it, then **Try it out** → **Execute**. You see the `curl` command it ran, the **Request URL**, and under **Server response**: **Code 200** and the **Response body** `{"message": "Welcome to Diamond Shop"}`.
- **Laravel needs a package (Scribe, L5-Swagger) and annotations for this.** FastAPI does it from your type hints, and it's never out of date. `/redoc` shows the same API in a second, read-only style.
- **Use `/docs` as your Postman** for the whole phase: it can send bodies, headers and files.
- The page loads its JavaScript from the internet (cdn.jsdelivr.net), so `/docs` is blank when you're offline. `/openapi.json` still works.

## Step 5: A second route, and the auto-reload

Add this route at the end of `main.py` and **save**:
```python
@app.get("/grades")
def grades() -> dict[str, list[str]]:
    return {
        "cut": ["Fair", "Good", "Very Good", "Premium", "Ideal"],
        "color": ["J", "I", "H", "G", "F", "E", "D"],
        "clarity": ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"],
    }
```
The server terminal prints `WARNING:  WatchFiles detected changes in 'main.py'. Reloading...` and restarts. Then:
```http
GET http://127.0.0.1:8001/grades
```
```
200 OK
{
  "cut": [
    "Fair",
    "Good",
    "Very Good",
    "Premium",
    "Ideal"
  ],
  "color": [
    "J",
    "I",
    "H",
    "G",
    "F",
    "E",
    "D"
  ],
  "clarity": [
    "I1",
    "SI2",
    "SI1",
    "VS2",
    "VS1",
    "VVS2",
    "VVS1",
    "IF"
  ]
}
```
- **No restart needed:** save the file and the server reloads by itself. Refresh `/docs` and **GET /grades** is there too.
- **The lists go from worst to best**, the same order as Task 6's `OrdinalEncoder`. A shop website could use this route to fill its drop-down menus.
- **`dict[str, list[str]]`:** string keys, and each value is a list of strings.
- **Two blank lines between functions** (PEP 8, Ruff E302/E305), as in Task 4.

## Recap
- A FastAPI app = `app = FastAPI()` + functions with `@app.get(...)` decorators. Return a dict, get JSON.
- `fastapi dev main.py --port 8001` (≈ `php artisan serve`) reloads on save. Always port 8001.
- `/docs` is free, interactive documentation built from your code; use it to try every request. `/openapi.json` is the same description as data.
- In PowerShell, use `curl.exe` for quick GETs and `/docs` for anything with a body.

📚 **Learn more:** [FastAPI: First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) · [FastAPI CLI (`fastapi dev` / `fastapi run`)](https://fastapi.tiangolo.com/fastapi-cli/) · [Concurrency and async / await](https://fastapi.tiangolo.com/async/) · [HTTP status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

Then commit, push, and ask Claude for **"check, then ex 2"** (path and query parameters).
