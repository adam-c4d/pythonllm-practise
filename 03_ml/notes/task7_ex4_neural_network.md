# Task 7, Exercise 4: A neural network with nn.Module, an optimizer and mini-batches (worked example)

Continue in `03_ml/pytorch_basics.ipynb`. Add a Markdown cell `## Exercise 4: A neural network for diamond prices`, then type these cells. The outputs are real (run on 2026-11-05). Training numbers may differ slightly on another computer or PyTorch version, and the training time depends on your CPU.

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
import time
from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
```

**What changes since Exercise 3:**

| Exercise 3 (by hand) | Exercise 4 (the usual PyTorch way) |
|---|---|
| 2 tensors, `w` and `b` | an `nn.Module` class with 3,649 weights in layers |
| `w -= lr * w.grad` for each weight | `optimizer.step()` updates all of them |
| `w.grad.zero_()` for each weight | `optimizer.zero_grad()` |
| all 43,152 rows in every step | **mini-batches** of 256 rows from a `DataLoader` |
| 1 feature (carat) | all 6 features → 23 numbers |

## Cell 1: Prepare the data (scikit-learn does the cleaning)

```python
def to_tensor(array):
    return torch.tensor(array, dtype=torch.float32)


def log_target(prices):
    return to_tensor(np.log(prices.to_numpy())).reshape(-1, 1)


X_fit, X_val, y_fit, y_val = train_test_split(
    X_train, y_train, test_size=0.2, random_state=42
)
log_then_scale = Pipeline([
    ("log", FunctionTransformer(np.log)),
    ("scale", StandardScaler()),
])
diamond_prep = ColumnTransformer([
    ("carat", log_then_scale, ["carat"]),
    ("num", StandardScaler(), ["depth", "table"]),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
     ["cut", "color", "clarity"]),
])
X_fit_t = to_tensor(diamond_prep.fit_transform(X_fit))
X_val_t = to_tensor(diamond_prep.transform(X_val))
X_test_t = to_tensor(diamond_prep.transform(X_test))
y_fit_t, y_val_t = log_target(y_fit), log_target(y_val)
print("fit:", X_fit_t.shape, " validation:", X_val_t.shape, " test:", X_test_t.shape)
print(X_fit_t[0])
```
```
fit: torch.Size([34521, 23])  validation: torch.Size([8631, 23])  test: torch.Size([10788, 23])
tensor([ 0.9249, -0.6594,  3.3801,  0.0000,  1.0000,  0.0000,  0.0000,  0.0000,
         0.0000,  0.0000,  1.0000,  0.0000,  0.0000,  0.0000,  0.0000,  0.0000,
         0.0000,  0.0000,  1.0000,  0.0000,  0.0000,  0.0000,  0.0000])
```
- **2 small helpers** replace Exercise 3's long `torch.tensor(..., dtype=torch.float32)` lines. `log_target` logs the prices and makes them one column.
- **A validation set:** the training diamonds are split again, 80/20, into **fit** (34,521, to learn from) and **validation** (8,631, to watch during training). The test set stays untouched until the very end, as in Task 5. You'll use the validation loss to see whether the network is still improving or starting to overfit.
- **The same cleaning as Task 6, with scikit-learn:** log + scale for carat, scale for depth and table, one-hot for the grades. `fit_transform` learns the means and categories from the fit rows only (no leakage), then `transform` reuses them.
- **`sparse_output=False`:** `OneHotEncoder` normally returns a "sparse" matrix that stores only the 1s. `torch.tensor` needs a normal (dense) array, so ask for one.
- **Neural networks need scaled inputs even more than logistic regression did.** Gradient descent takes steps of the same size for every weight, and it works best when every input is around 0 with a similar spread. **23 columns:** 3 numbers + 5 cuts + 7 colours + 8 clarities.

## Cell 2: The model is a class

```python
class PriceNet(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(n_features, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.layers(x)


def count_params(model):
    return sum(p.numel() for p in model.parameters())


torch.manual_seed(42)
untrained = PriceNet(X_fit_t.shape[1])
print(untrained)
print("Parameters:", count_params(untrained))
print("Untrained predictions:", untrained(X_fit_t[:3]).squeeze(1))
```
```
PriceNet(
  (layers): Sequential(
    (0): Linear(in_features=23, out_features=64, bias=True)
    (1): ReLU()
    (2): Linear(in_features=64, out_features=32, bias=True)
    (3): ReLU()
    (4): Linear(in_features=32, out_features=1, bias=True)
  )
)
Parameters: 3649
Untrained predictions: tensor([0.2311, 0.1675, 0.2198], grad_fn=<SqueezeBackward1>)
```
- **`class PriceNet(nn.Module)`** is how every PyTorch model is written, from this one to Llama. Laravel analogy: it's like `class Diamond extends Model`. You inherit all the machinery (here: finding the weights, saving, `train()` / `eval()`) and only describe your own parts. **`super().__init__()`** must come first, like calling `parent::__construct()`.
- **`__init__` lists the layers, `forward` says how data flows through them.** You never call `forward` yourself: `untrained(x)` calls it for you, the way PHP calls `__invoke()` when you use an object like a function.
- **`nn.Linear(23, 64)`** is `X @ w + bias` from Exercise 1 with 23 × 64 weights + 64 biases: 64 different weighted sums of the 23 inputs. **`nn.Sequential`** chains layers, so the output of one is the input of the next: 23 → 64 → 32 → 1 number, the log price.
- **`nn.ReLU()`** ("rectified linear unit") replaces every negative number with 0. That small bend is what makes it a *neural network*: without it, 3 linear layers in a row would still be just one straight line. With it, the network can learn curves and combinations such as "big **and** clear costs extra". A network with layers between the input and output like this is called an **MLP** (multi-layer perceptron); the middle layers are **hidden layers**.
- **3,649 parameters:** (23 × 64 + 64) + (64 × 32 + 32) + (32 + 1). They all start random, so the untrained predictions are near 0, far from the real log prices of about 7.8. `grad_fn` shows PyTorch is recording, ready for `backward()`.

## Cell 3: Mini-batches with a DataLoader

```python
fit_data = TensorDataset(X_fit_t, y_fit_t)
print("rows:", len(fit_data))
loader = DataLoader(fit_data, batch_size=256, shuffle=True,
                    generator=torch.Generator().manual_seed(42))
xb, yb = next(iter(loader))
print("one batch:", xb.shape, yb.shape, " batches per epoch:", len(loader))
```
```
rows: 34521
one batch: torch.Size([256, 23]) torch.Size([256, 1])  batches per epoch: 135
```
- **`TensorDataset`** pairs the inputs with their targets, row by row: `fit_data[0]` is the first diamond's 23 numbers and its log price.
- **`DataLoader` hands out batches of 256 rows**, in a new random order each pass (`shuffle=True`). Laravel analogy: it's `Diamond::inRandomOrder()->chunk(256, ...)`.
- **Why mini-batches?** One update per 256 rows means **135 updates per pass** instead of 1, so the model learns much faster. Each batch's gradient is a bit noisy, but that noise even helps a little. And with millions of rows (or images), the whole data set wouldn't fit in memory anyway.
- **`generator=torch.Generator().manual_seed(42)`** fixes the shuffle order, so your numbers match these notes. One full pass over all batches is called an **epoch**.
- **`next(iter(loader))`** takes just the first batch, to look at its shape: `(256, 23)` inputs and `(256, 1)` targets.

## Cell 4: Train

```python
torch.manual_seed(42)
price_net = PriceNet(X_fit_t.shape[1])
optimizer = torch.optim.Adam(price_net.parameters(), lr=0.001)
loss_fn = nn.MSELoss()
loader = DataLoader(fit_data, batch_size=256, shuffle=True,
                    generator=torch.Generator().manual_seed(42))
history = []
start = time.perf_counter()
for epoch in range(1, 31):
    price_net.train()
    epoch_loss = 0.0
    for xb, yb in loader:
        loss = loss_fn(price_net(xb), yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item() * len(xb)
    price_net.eval()
    with torch.no_grad():
        val_loss = loss_fn(price_net(X_val_t), y_val_t).item()
    history.append({"epoch": epoch, "train": epoch_loss / len(fit_data),
                    "validation": val_loss})
    if epoch in (1, 2, 5) or epoch % 10 == 0:
        print(f"epoch {epoch:2d}   train loss {history[-1]['train']:.4f}   "
              f"validation loss {val_loss:.4f}")
print(f"PriceNet trained in {time.perf_counter() - start:.1f} s")
```
```
epoch  1   train loss 19.4013   validation loss 0.2481
epoch  2   train loss 0.1588   validation loss 0.0929
epoch  5   train loss 0.0402   validation loss 0.0304
epoch 10   train loss 0.0184   validation loss 0.0174
epoch 20   train loss 0.0138   validation loss 0.0142
epoch 30   train loss 0.0128   validation loss 0.0134
PriceNet trained in 12.3 s
```
- **The same 5 steps as Exercise 3**, now per batch: forward (`price_net(xb)`), loss, `zero_grad()`, `backward()`, `step()`. Resetting *before* `backward()` instead of after works the same way, and it's the usual order in PyTorch code.
- **`torch.optim.Adam`** is the optimizer: it does `w -= lr * w.grad` for all 3,649 weights, with one improvement. It adapts the step size for each weight, using the size of its recent gradients. **Adam with `lr=0.001`** is the standard first choice, much like `HistGradientBoostingRegressor` with its defaults in Task 6.
- **`nn.MSELoss()`** is Exercise 3's `((pred - y) ** 2).mean()`, ready-made.
- **The model, the optimizer and the loader are all created in this cell, after the seed.** Rerun the cell and you get the same numbers. If the model came from an earlier cell, a rerun would keep training the already-trained model.
- **`train()` and `eval()`** switch the model between training and prediction mode. This model behaves the same in both, but layers such as dropout don't, so the habit matters. **`torch.no_grad()`** skips the recording when you only measure.
- **Epoch 1's train loss is huge (19.4)** because the network starts by predicting about 0 for log prices of about 7.8. It's the average over the whole epoch, *while* the network was improving. The validation loss is measured at the *end* of the epoch, which is why it's lower at first.
- **From epoch 10, both losses fall slowly and stay close together:** no overfitting. A validation loss of 0.0134 means a typical error of about √0.0134 ≈ 0.12 in log units, roughly **±12%** of the price.
- **About 10 s for 30 epochs** on this PC (8–12 s in different runs, 6 cores): 30 × 135 = 4,050 updates of 3,649 weights each. The time is printed with `time.perf_counter()` (Task 6), and yours will differ.

## Cell 5: Look at the loss curves

```python
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
curves = pd.DataFrame(history)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(curves["epoch"], curves["train"], color="#2a78d6", linewidth=2,
        label="training")
ax.plot(curves["epoch"], curves["validation"], color="#eb6834", linewidth=2,
        label="validation")
ax.set(yscale="log", xlabel="Epoch", ylabel="Loss (MSE of log price, log scale)",
       title="The loss falls fast, then flattens; validation stays close to training")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.savefig(output_dir / "loss_curve.png", bbox_inches="tight")
plt.show()
```
The chart: a blue training line that drops steeply from 19.4 (epoch 1) to 0.16 (epoch 2), and an orange validation line that starts at 0.25. From about epoch 10 both lines run almost on top of each other, flattening at about 0.013.

- **This chart is the first thing to look at after any training run.** It answers 3 questions: is it learning (falling), is it done (flat), is it overfitting (validation going up while training goes down)?
- **`yscale="log"`**, because the loss falls from about 19 to about 0.013: on a normal axis, everything after epoch 2 would be a flat line at the bottom.
- **2 series, so there's a legend.** The colours match the rest of the course: blue for the first series, orange for the second.

## Cell 6: Test MAE in dollars

```python
price_net.eval()
with torch.no_grad():
    net_pred = torch.exp(price_net(X_test_t)).squeeze(1).numpy()
print(f"Neural net test MAE: ${mean_absolute_error(y_test, net_pred):,.0f}")
```
```
Neural net test MAE: $336
```
- **`torch.exp` turns the predicted log prices into dollars**, and `.numpy()` makes them an array for scikit-learn's `mean_absolute_error`.
- **How it compares (test MAE on the same 10,788 diamonds):**

  | Model | Test MAE |
  |---|---|
  | baseline (always the mean), Task 6 | $3,021 |
  | straight line on carat, Task 6 | $1,010 |
  | line on log carat, Exercise 3 | $839 |
  | linear on log scales, all features, Task 6 | $400 |
  | **this neural network** | **$336** |
  | tuned gradient boosting, Task 6 | **$285** |

- **The network beats every linear model** ($336 vs $400), because ReLU lets it learn curves and combinations of features. **But gradient boosting still wins** ($285), with less code, no scaling, and under a second of training.
- **More epochs or bigger layers don't close the gap.** In extra runs made for these notes (60 epochs; a 3× larger learning rate; 64 + 64 units with batches of 128), the test MAE stayed between $330 and $346. The network has learned about all it can from these 6 columns.
- **That's the usual result on tables** (rows and columns of mixed features). Trees split on one feature at a time, which suits columns that each mean something different (a weight, a grade, a percentage). Neural networks shine on **raw signals with many similar values**, such as pixels, sound waves or words, where no human can write the features (Exercise 6).

## Markdown answer cell

```markdown
## Exercise 4 answers
- **Data:** scikit-learn's `ColumnTransformer` (log + scale carat, scale depth and table, one-hot grades with `sparse_output=False`) → 23 float32 columns. Fit / validation / test = 34,521 / 8,631 / 10,788 rows.
- **Model:** `PriceNet(nn.Module)`: Linear 23 → 64, ReLU, Linear 64 → 32, ReLU, Linear 32 → 1. **3,649 parameters.** ReLU is what lets it learn curves.
- **Training:** `DataLoader` batches of 256 (135 per epoch, shuffle seeded), Adam lr 0.001, `MSELoss`, 30 epochs in about 10 s. Loss: train 19.4 → 0.0128, validation 0.248 → 0.0134 (about ±12% of the price).
- **Loss curves:** both fall fast and then flatten; validation stays close to training, so no overfitting.
- **Test MAE $336**: better than every linear model ($400 on log scales), worse than tuned gradient boosting ($285). On tables, boosting usually wins.
```

📚 **Learn more:** [Build the neural network (tutorial)](https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html) · [`nn.Module`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html) · [`nn.Linear`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html) · [`torch.optim.Adam`](https://docs.pytorch.org/docs/stable/generated/torch.optim.Adam.html) · [`DataLoader`](https://docs.pytorch.org/docs/stable/data.html)

Then commit, push, and ask Claude for **"check, then ex 5"** (classification: Titanic survival with a neural network).
