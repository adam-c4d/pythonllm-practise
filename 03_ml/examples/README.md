# 03_ml examples: reference solutions

These notebooks are the **finished versions of the worked examples** in [../notes/](../notes/), with their real outputs saved inside. You can read them right here on GitHub, or run them in VS Code.

**Type your own version first**, in your own notebook. Use these to compare your outputs, or when you're stuck.

| Notebook | Task | Your own notebook | Run time |
|---|---|---|---|
| [task5_titanic_model.ipynb](task5_titanic_model.ipynb) | Task 5: Titanic survival (classification) | `03_ml/titanic_model.ipynb` | about 20 s |
| [task6_diamond_prices.ipynb](task6_diamond_prices.ipynb) | Task 6: diamond prices (regression) | `03_ml/diamond_prices.ipynb` | about 30 s |
| [task7_pytorch_basics.ipynb](task7_pytorch_basics.ipynb) | Task 7: deep learning basics (PyTorch) | `03_ml/pytorch_basics.ipynb` | about 40 s |

## How to run one
1. Open the notebook in VS Code and choose the **dsllm** kernel.
2. **Restart → Run All.**

**Only the paths differ from the notes.** These notebooks live in `03_ml/examples/`, so the paths start with `../` (`../data/diamonds.csv`, `Path("../output")`, `Path("../models")`). Otherwise the code is exactly what the notes show.

They write their charts and models into the same `03_ml/output/` and `03_ml/models/` folders as your notebooks. The files come out identical to yours, because every random step uses `random_state=42` or `torch.manual_seed(42)`.

**Order matters for Task 7:** its Exercise 6 loads `03_ml/models/diamond_price_model.joblib`, which Task 6 Exercise 8 creates. On a new computer, run the Task 6 notebook first (yours or this one). Task 7 also needs PyTorch: see [SETUP.md](../../SETUP.md).
