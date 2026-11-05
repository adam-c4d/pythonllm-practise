# Task 7, Exercise 3: A training loop by hand (worked example)

Continue in `03_ml/pytorch_basics.ipynb`. Add a Markdown cell `## Exercise 3: A training loop by hand`, then type these cells. The outputs are real (run on 2026-11-05). Training numbers may differ slightly in the last digits on another computer or PyTorch version.

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
```

**The plan:** fit Task 6's best simple line, `log(price) = b + w × log(carat)`, but **without** scikit-learn's `fit()`. You write the 5 steps of Exercise 2 yourself and let gradient descent find `w` and `b`. Then you check the answer against `LinearRegression`. If both agree, you understand what every PyTorch training loop does.

## Cell 1: Diamonds as tensors

```python
df = pd.read_csv("data/diamonds.csv")
features = ["carat", "cut", "color", "clarity", "depth", "table"]
X_train, X_test, y_train, y_test = train_test_split(
    df[features], df["price"], test_size=0.2, random_state=42
)
log_carat = torch.tensor(np.log(X_train["carat"].to_numpy()), dtype=torch.float32)
log_carat = log_carat.reshape(-1, 1)
log_price = torch.tensor(np.log(y_train.to_numpy()), dtype=torch.float32)
log_price = log_price.reshape(-1, 1)
print(log_carat.shape, log_price.shape)
print("first 3 log carats:", log_carat[:3].squeeze(1))
print("first 3 log prices:", log_price[:3].squeeze(1))
```
```
torch.Size([43152, 1]) torch.Size([43152, 1])
first 3 log carats: tensor([0.6981, 0.0100, 0.0953])
first 3 log prices: tensor([9.6947, 8.4207, 8.6533])
```
- **The same split as Task 6** (`test_size=0.2, random_state=42`), so the 43,152 training diamonds are the same ones, and the results can be compared.
- **`.to_numpy()`** turns a pandas column into a NumPy array, and `torch.tensor(..., dtype=torch.float32)` turns that into a tensor (Exercise 1, Cell 3).
- **`np.log` on both sides**, because Task 6 Exercise 5 showed that price vs carat is a straight line on log scales. The first diamond weighs e^0.698 = 2.01 carats and costs e^9.695 = $16,231.
- **`reshape(-1, 1)` gives shape `(43152, 1)`**: one column, the shape a model's predictions will have. That avoids the `(n, n)` broadcasting bug from Exercise 1, Cell 8.

## Cell 2: The answer to check against

```python
line = LinearRegression().fit(log_carat.numpy(), log_price.numpy())
slope, intercept = line.coef_[0][0], line.intercept_[0]
print(f"scikit-learn: slope {slope:.4f}, intercept {intercept:.4f}")
```
```
scikit-learn: slope 1.6780, intercept 8.4502
```
- **`LinearRegression` solves this with one formula** (least squares, Task 6 Exercise 2). Its answer is the exact best line, so it's the target for your loop.
- **`.numpy()` turns the tensors back** into arrays, because scikit-learn doesn't take tensors.
- **`coef_[0][0]`:** with a 2-D `y`, scikit-learn returns the weights as a table (one row per target), so you need 2 indexes.

## Cell 3: The training loop

```python
torch.manual_seed(42)
w = torch.randn(1, requires_grad=True)
b = torch.randn(1, requires_grad=True)
lr = 0.1
for step in range(301):
    pred = log_carat * w + b  # 1. forward: predict every diamond
    loss = ((pred - log_price) ** 2).mean()  # 2. loss: mean squared error
    if step % 50 == 0:
        print(f"step {step:3d}   loss {loss.item():8.4f}   "
              f"w {w.item():.4f}   b {b.item():.4f}")
    loss.backward()  # 3. backward: compute the gradients
    with torch.no_grad():  # 4. update: one step downhill
        w -= lr * w.grad
        b -= lr * b.grad
    w.grad.zero_()  # 5. reset the gradients for the next step
    b.grad.zero_()
```
```
step   0   loss  61.4110   w 0.3367   b 0.1288
step  50   loss   0.0925   w 1.4247   b 8.3115
step 100   loss   0.0692   w 1.6638   b 8.4424
step 150   loss   0.0692   w 1.6772   b 8.4497
step 200   loss   0.0692   w 1.6779   b 8.4502
step 250   loss   0.0692   w 1.6780   b 8.4502
step 300   loss   0.0692   w 1.6780   b 8.4502
```
- **`torch.manual_seed(42)` fixes the random start**, like `random_state=42` in scikit-learn. `torch.randn(1)` draws one random number from a bell curve around 0. Without the seed, every run would start (and end) slightly differently.
- **Step 0 has a huge loss (61.4)** because the random start predicts a log price near 0, but real log prices are about 7.8: (7.8)² ≈ 61.
- **The loss falls to 0.0692 and stops falling.** That's the bottom of the hill. `w` and `b` stop changing after about 200 steps.
- **This is the loop inside every PyTorch model**, and it doesn't change in Exercises 4 and 5. Only the model (step 1) and the tools for steps 4 and 5 (an optimizer) become fancier. Laravel analogy: it's like a queue worker's loop: take a job, process it, record the result, clean up, repeat.
- **`pred - log_price` uses all 43,152 diamonds at once.** Each step is one matrix operation, not a Python loop over rows, so 300 steps take a fraction of a second.

## Cell 4: Compare, then price the test diamonds

```python
print(f"PyTorch:      slope {w.item():.4f}, intercept {b.item():.4f}")
print(f"scikit-learn: slope {slope:.4f}, intercept {intercept:.4f}")
test_log_carat = torch.tensor(np.log(X_test["carat"].to_numpy()), dtype=torch.float32)
with torch.no_grad():
    test_pred = torch.exp(test_log_carat.reshape(-1, 1) * w + b).squeeze(1)
print(f"Test MAE: ${mean_absolute_error(y_test, test_pred.numpy()):,.0f}")
print(f"Twice the carat → {2 ** w.item():.1f}× the price")
```
```
PyTorch:      slope 1.6780, intercept 8.4502
scikit-learn: slope 1.6780, intercept 8.4502
Test MAE: $839
Twice the carat → 3.2× the price
```
- **The loop found the same line as scikit-learn**, to 4 decimals. Gradient descent and the least-squares formula are two roads to the same answer. For a line, the formula is faster. For a neural network, there's no formula, and gradient descent is the only road.
- **`torch.exp` turns log prices back into dollars**, the job `TransformedTargetRegressor` did for you in Task 6. `squeeze(1)` makes it a flat list of 10,788 prices for `mean_absolute_error`.
- **Test MAE $839 with only the carat.** Task 6's straight line on plain carat was $1,010. The right *shape* (logs) helps even with one feature.
- **Twice the carat → 3.2× the price.** With all the grades in the model (Task 6 Exercise 5) it was 3.7×. Big diamonds tend to have worse colour and clarity, so carat alone hides part of its own effect (confounding, Task 6 Exercise 4).

## Markdown answer cell

```markdown
## Exercise 3 answers
- **Data:** log carat and log price of the 43,152 training diamonds (Task 6 split), as float32 tensors of shape `(43152, 1)`.
- **The 5 steps:** forward (`log_carat * w + b`) → loss (mean squared error) → `backward()` → update inside `torch.no_grad()` → reset the gradients. Seed 42, learning rate 0.1, 300 steps.
- **Loss:** 61.4 at step 0 (random start), **0.0692** from step 100; `w` and `b` settle by step 250.
- **Result:** slope **1.6780**, intercept **8.4502**, the same as `LinearRegression` to 4 decimals.
- **Test MAE $839** with carat only (Task 6's plain line: $1,010). Twice the carat = 3.2× the price.
```

📚 **Learn more:** [`torch.manual_seed`](https://docs.pytorch.org/docs/stable/generated/torch.manual_seed.html) · [`torch.randn`](https://docs.pytorch.org/docs/stable/generated/torch.randn.html) · [Optimizing model parameters (tutorial)](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)

Then commit, push, and ask Claude for **"check, then ex 4"** (a real neural network with `nn.Module`, an optimizer and mini-batches).
