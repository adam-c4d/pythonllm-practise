# How companies deploy Python AI / ML / FastAPI projects

Background reading for the January "job-ready" step (Docker and deployment).
Asked on 2026-11-04.

## The one idea to remember

Almost everything ships as a **Docker container** that runs in the cloud. The type of project
changes; the delivery line stays the same:

```
git push → CI (GitHub Actions: ruff + pytest) → build Docker image → push image to a registry
        → cloud platform runs the image → logs, errors and monitoring
```

**Laravel analogy:** it's like Forge or Envoyer deploying on push. The difference is what you
ship. With Laravel you copy files to a server that already has PHP. With Python you ship a sealed
box (the *image*) that holds Python, every library and your code.

**Why containers?** Python dependencies are fragile. Numpy, pandas and scikit-learn depend on
compiled C libraries. You've already seen this: the `mkl_rt.2.dll` crash, where the wrong DLL got
loaded. A container fixes "works on my machine", because the server runs exactly the box you
built and tested.

## The big difference from PHP: Python apps stay running

- **PHP** (php-fpm): each request starts fresh and forgets everything when it finishes.
- **Python** (uvicorn): the app is one **long-running process**. Anything you load at startup
  stays in memory for every later request.

That's why serving an ML model from FastAPI is easy: you load the `.joblib` file **once** at
startup, and every `/predict` request reuses it. It also means memory use matters, because a big
model sits in RAM the whole time.

---

## 1. FastAPI APIs

**How it runs:** `fastapi run main.py` starts **uvicorn**, an ASGI server (≈ php-fpm), usually
with several workers. A load balancer or nginx sits in front and handles HTTPS.

**Where it runs, from small to big:**

| Option | Examples | Laravel equivalent | Who uses it |
|---|---|---|---|
| Platform as a service | Render, Railway, Fly.io, Heroku | Forge / Laravel Cloud | Start-ups, side projects, portfolios |
| Serverless containers | **Google Cloud Run**, **AWS ECS Fargate**, **Azure Container Apps** | — | **Most common in companies.** You give it an image; it scales up and down for you |
| Kubernetes | AWS EKS, Google GKE, Azure AKS | — | Big companies with a platform/DevOps team |
| Serverless functions | AWS Lambda (with the `mangum` adapter) | Laravel Vapor | Small, spiky APIs |
| Your own VPS | DigitalOcean, Hetzner + Docker Compose | Your own Laravel VPS | Small teams, cheap |

**A typical Dockerfile** (you'll write one in January; not run here because Docker isn't installed yet):

```dockerfile
FROM python:3.13-slim                 # base image: Linux + Python, nothing else
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # install libraries first (cached layer)
COPY . .                              # then copy your code
CMD ["fastapi", "run", "main.py", "--port", "8000"]  # production mode (not `fastapi dev`)
```

**Why `requirements.txt` gets copied before the code:** Docker caches each step. Your code changes
often but your libraries rarely do, so the slow `pip install` step is reused on most builds.

---

## 2. Machine-learning models (scikit-learn)

ML has **two halves** that run at different times: **training** and **serving**.

**Training** (offline, not part of the web app):
notebook (explore) → `train.py` script → run as a job → produces a model file (`model.joblib`,
which you'll make in Task 5 Ex 8) → stored in cloud storage (AWS S3) or a **model registry** such
as MLflow, with its version and test scores.

**Serving** comes in three common patterns:

| Pattern | How it works | Laravel equivalent | When it's used |
|---|---|---|---|
| **a. Inside FastAPI** | Load the `.joblib` at startup and expose `/predict` | A controller that calls a service class | **Most common for scikit-learn.** This is your capstone |
| **b. Batch** | A nightly job scores every row (e.g. churn risk for all customers) and writes the results to a database table; the app just reads that table | A scheduled Artisan command | Very common. Fast, simple, and nothing can break at request time |
| **c. Managed endpoint** | The cloud hosts the model for you: AWS SageMaker, Google Vertex AI, Azure ML | — | Bigger ML teams, deep-learning models |

**Things that go wrong in production:**
- **Version mismatch:** train with scikit-learn 1.x and serve with a different version, and
  loading the model warns or breaks. Pin versions in `requirements.txt`.
- **Data drift:** real-world data slowly changes, so accuracy drops. Teams monitor it and retrain.
- **Deep-learning models** (PyTorch) need GPUs, so they go on GPU servers or managed endpoints.

---

## 3. LLM apps (the AI Engineer job you're aiming for)

**Most companies do not host the LLM themselves.** Their app is a FastAPI service that *calls* a
model over HTTP:

- **Directly:** the OpenAI, Anthropic or Google Gemini APIs.
- **Through their cloud:** AWS Bedrock, Azure OpenAI / Azure AI Foundry, Google Vertex AI.
  Enterprises like this because data, contracts and billing stay with a cloud provider they
  already use.

So **deploying an LLM app = deploying a FastAPI app (section 1)** plus a few extra parts:

| Part | Common tools | Laravel equivalent |
|---|---|---|
| API key | Kept in a secrets manager, read as an env var | `.env` → `config()` |
| Vector database (for RAG) | **pgvector in Postgres** (most common; it's plain SQL), Pinecone, Qdrant | MySQL with an extra column type |
| Slow background work (e.g. embedding 1,000 PDFs) | Celery or arq + Redis | Queues + Horizon |
| Streaming answers word by word | Server-Sent Events (`StreamingResponse`) | — |
| Tracing every prompt, response, cost and latency | Langfuse, LangSmith | Telescope, but for LLM calls |
| Checking answer quality | **Evals** (automated tests of LLM output) | Feature tests |

**Self-hosting open models** (Llama, Mistral, Qwen) happens only when privacy, cost or volume
demand it. That means GPU servers running a serving engine such as **vLLM**, on Kubernetes with
GPU nodes or on GPU clouds (Modal, RunPod, Hugging Face Inference Endpoints). **Ollama** (Phase 5)
is mainly for local development, not large-scale production.

---

## 4. Plain Python scripts and data jobs

These aren't websites, so they aren't "served"; they **run on a schedule**:

| Option | Laravel equivalent |
|---|---|
| cron on a server, Kubernetes CronJob, Cloud Run Jobs, AWS Lambda + EventBridge schedule | `$schedule->command(...)` + `schedule:run` |
| **Orchestrators** for multi-step pipelines with retries: Airflow, Dagster, Prefect | Job chains / batches, but much bigger |
| Data platforms: Databricks, Snowflake, BigQuery (run SQL and Python jobs on huge data) | — |

---

## 5. Notebooks, dashboards and demos

- **Notebooks are not deployed.** They are for exploring. When code goes to production it moves
  into `.py` files, which is what you did in Task 3 Ex 5 (notebook → `report_pandas.py`).
- **Internal dashboards and demo UIs:** Streamlit or Gradio, hosted on Streamlit Community Cloud,
  Hugging Face Spaces or an internal server. These are handy for portfolio demos, because a
  recruiter can click a link and try your model.

---

## Laravel ↔ Python cheat sheet

| Laravel / PHP | Python |
|---|---|
| `php artisan serve` | `fastapi dev` |
| php-fpm + nginx | uvicorn (`fastapi run`) + nginx / load balancer |
| `composer.json` + `composer.lock` | `requirements.txt`, or `pyproject.toml` + `uv.lock` (the `uv` tool is popular) |
| `.env` | `.env` locally; a secrets manager in production (AWS Secrets Manager, Azure Key Vault) |
| PHPUnit | pytest |
| PHP-CS-Fixer / PHPStan | Ruff / mypy |
| Queues + Horizon | Celery / arq + Redis |
| Scheduler | cron, Cloud Run Jobs, Airflow |
| Forge / Laravel Cloud | Render / Railway |
| Vapor | AWS Lambda + Mangum |
| Sentry | Sentry (same tool) |

## What AI Engineer job ads usually ask for

Python, **FastAPI**, **Docker**, **one cloud** (AWS appears most often; Azure is common in
companies that run on Microsoft), **CI/CD** (GitHub Actions), **Postgres + pgvector**, LLM APIs,
RAG, **evals**. Kubernetes and Terraform (infrastructure described in code files) are nice to have.

## Where this fits in your plan

Task 5 Ex 8: save a `.joblib` → Phase 4: serve it from FastAPI → Phase 5: call an LLM API →
Capstone: "Ask Your Data" API → **January: Dockerfile + GitHub Actions + deploy the capstone to a
real URL** (e.g. Render or Cloud Run). A live link on your CV shows you can ship, not just code
in notebooks.
