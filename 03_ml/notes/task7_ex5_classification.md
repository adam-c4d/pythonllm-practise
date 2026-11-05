# Task 7, Exercise 5: Classification, Titanic survival with a neural network (worked example)

Continue in `03_ml/pytorch_basics.ipynb`. Add a Markdown cell `## Exercise 5: Titanic survival with a neural network`, then type these cells. The outputs are real (run on 2026-11-05). Training numbers may differ slightly on another computer or PyTorch version.

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
from sklearn.impute import SimpleImputer
```

**What changes for yes/no answers:** the network still outputs one number per row, but now it's a **logit**, a score where positive means "survived" and negative means "died". The sigmoid squeezes it into a probability between 0 and 1, exactly as in Task 5's logistic regression. Only the last step and the loss change; the training loop stays the same.

## Cell 1: Task 5's data, split and cleaning, as tensors

```python
titanic = pd.read_csv("../02_data/data/titanic.csv")
numeric = ["pclass", "age", "sibsp", "parch", "fare"]
categorical = ["sex", "embarked"]
X_train, X_test, y_train, y_test = train_test_split(
    titanic[numeric + categorical], titanic["survived"],
    test_size=0.2, random_state=42, stratify=titanic["survived"],
)
titanic_prep = ColumnTransformer([
    ("num", Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), numeric),
    ("cat", Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ]), categorical),
])
X_train_t = to_tensor(titanic_prep.fit_transform(X_train))
X_test_t = to_tensor(titanic_prep.transform(X_test))
y_train_t = to_tensor(y_train.to_numpy()).reshape(-1, 1)
y_test_t = to_tensor(y_test.to_numpy()).reshape(-1, 1)
print("train:", X_train_t.shape, " test:", X_test_t.shape)
print(f"survival rate: train {y_train_t.mean():.1%}, test {y_test_t.mean():.1%}")
```
```
train: torch.Size([712, 10])  test: torch.Size([179, 10])
survival rate: train 38.3%, test 38.5%
```
- **The same split as Task 5** (`test_size=0.2, random_state=42, stratify=y`), so it's the same 712 and 179 passengers. The survival rates (38.3% and 38.5%) match Task 5 Exercise 1.
- **The same cleaning as Task 5 Exercise 5:** median + scaling for the numbers, most frequent + one-hot for the text. 7 columns become 10. Again `sparse_output=False`, because `torch.tensor` needs a dense array.
- **This reuses `X_train`, `X_test`, `y_train` and `y_test`**, so the diamond versions are overwritten. That's fine: Exercise 6 only needs `price_net`, `diamond_prep` and `to_tensor`, which keep their names.
- **The targets are 0.0 / 1.0 floats**, shape `(712, 1)`. The loss function in Cell 3 needs floats, not whole numbers.

## Cell 2: Logits, sigmoid, and the 0.5 cut-off

```python
logits = torch.tensor([-3.0, 0.0, 2.0])
print("logits:       ", logits)
print("probabilities:", torch.sigmoid(logits))
print("predictions:  ", (torch.sigmoid(logits) >= 0.5).int())
```
```
logits:        tensor([-3.,  0.,  2.])
probabilities: tensor([0.0474, 0.5000, 0.8808])
predictions:   tensor([0, 1, 1], dtype=torch.int32)
```
- **`torch.sigmoid`** is the S-shaped squeeze from Task 5: very negative → near 0, 0 → exactly 0.5, very positive → near 1.
- **The 0.5 cut-off** turns a probability into a yes/no answer, like scikit-learn's `predict()` does. A logit of 0 is exactly 0.5, so "logit ≥ 0" and "probability ≥ 0.5" give the same predictions.
- **A logistic regression is a neural network with no hidden layer:** `nn.Linear(10, 1)` + sigmoid. The network in Cell 3 adds one hidden layer of 16 units with ReLU in between.

## Cell 3: A training function

```python
def accuracy(net, X_t, y_t):
    with torch.no_grad():
        predictions = (torch.sigmoid(net(X_t)) >= 0.5).float()
    return (predictions == y_t).float().mean().item()


def train_survival_net(seed, epochs=50, verbose=False):
    torch.manual_seed(seed)
    net = nn.Sequential(nn.Linear(X_train_t.shape[1], 16), nn.ReLU(), nn.Linear(16, 1))
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    loss_fn = nn.BCEWithLogitsLoss()
    loader = DataLoader(TensorDataset(X_train_t, y_train_t), batch_size=32,
                        shuffle=True, generator=torch.Generator().manual_seed(seed))
    for epoch in range(1, epochs + 1):
        net.train()
        for xb, yb in loader:
            loss = loss_fn(net(xb), yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        net.eval()
        if verbose and epoch % 10 == 0:
            with torch.no_grad():
                train_loss = loss_fn(net(X_train_t), y_train_t).item()
            print(f"epoch {epoch}   train loss {train_loss:.4f}   "
                  f"train accuracy {accuracy(net, X_train_t, y_train_t):.1%}")
    return net


survival_net = train_survival_net(seed=42, verbose=True)
```
```
epoch 10   train loss 0.5012   train accuracy 77.8%
epoch 20   train loss 0.4271   train accuracy 82.9%
epoch 30   train loss 0.4100   train accuracy 82.4%
epoch 40   train loss 0.4009   train accuracy 82.9%
epoch 50   train loss 0.3947   train accuracy 83.8%
```
- **`nn.BCEWithLogitsLoss`** ("binary cross-entropy") is the loss for yes/no answers. It applies the sigmoid itself, then punishes confident wrong answers hard: saying 99% "survived" for someone who died costs far more than saying 60%. It's the same loss logistic regression minimises.
- **Give it logits, not probabilities.** That's why the network has no sigmoid at the end: `BCEWithLogitsLoss` does the sigmoid inside, in a way that can't overflow. Add `torch.sigmoid` only when you want probabilities (Cell 4).
- **`nn.Sequential` without a class** is fine for a simple stack of layers. Write a class (Exercise 4) when you need your own `forward`, or a name you can rebuild later (Exercise 6).
- **A function, so you can train again with another seed** (Cell 5). It's the Task 5 `make_model()` idea: one place that builds a fresh model. Laravel analogy: a service class with one public method, instead of copy-pasted controller code.
- **Smaller batches (32), because there are only 712 rows:** that's 23 updates per epoch. The loss falls and the training accuracy rises to about 84%.

## Cell 4: The test set, once

```python
with torch.no_grad():
    test_proba = torch.sigmoid(survival_net(X_test_t)).squeeze(1)
print("first 5 chances:", test_proba[:5].numpy().round(2))
print("first 5 actual: ", y_test_t[:5].squeeze(1).int().numpy())
test_acc = accuracy(survival_net, X_test_t, y_test_t)
correct = round(test_acc * len(y_test_t))
print(f"Test accuracy: {test_acc:.1%} ({correct} of {len(y_test_t)} passengers)")
```
```
first 5 chances: [0.09 0.09 0.19 0.05 0.68]
first 5 actual:  [0 0 1 0 1]
Test accuracy: 79.3% (142 of 179 passengers)
```
- **Probabilities, then the cut-off:** passengers under 0.5 are predicted to die. The first 5 are the same passengers as in Task 5 Exercise 2, and the network makes the same 1 mistake: the 3rd passenger survived but gets only a 19% chance.
- **`.numpy().round(2)`** prints the chances as a short NumPy list. A tensor would print 4 decimals (`0.0900`) even after rounding.
- **How it compares on the same 179 passengers:**

  | Model (Task 5) | Test accuracy |
  |---|---|
  | baseline (always "died") | 61.5% |
  | logistic regression, all 7 features (Exercise 5) | 80.4% (144) |
  | tuned random forest (Exercise 7) | 79.9% (143) |
  | **this neural network** | **79.3% (142)** |

- **The network is 2 passengers behind logistic regression.** With 179 test passengers, 1 passenger is 0.56 percentage points, so these 3 models are too close to call (the Task 5 lesson).

## Cell 5: How much does the seed matter?

```python
rows = []
for seed in range(5):
    net = train_survival_net(seed)
    rows.append({"seed": seed,
                 "train": accuracy(net, X_train_t, y_train_t),
                 "test": accuracy(net, X_test_t, y_test_t)})
display(pd.DataFrame(rows).set_index("seed").round(3))
```
```
      train   test
seed              
0     0.824  0.816
1     0.838  0.816
2     0.837  0.810
3     0.834  0.821
4     0.822  0.827
```
- **The same network and the same data, with only a different random start and shuffle:** the test accuracy goes from **81.0% to 82.7%** (145 to 148 passengers), and seed 42 gave 79.3% (142). Logistic regression has no random start, so it gives the same 80.4% every time.
- **So seed 42 was a bit unlucky.** The 6 runs average 81.4%, about 2 passengers more than logistic regression. That's still within the noise of a 179-row test set.
- **Don't pick the seed with the best test score.** That's tuning on the exam (Task 5 Exercise 7). This cell only shows how much luck is in a single number. To compare models fairly, use cross-validation, and for a network, average a few seeds.
- **The honest lesson: small tables don't need deep learning.** With 712 rows and 7 columns, the network does about as well as logistic regression, no clear win. It needs more code and more settings (layers, learning rate, epochs, batch size), its result depends on the seed, and its weights can't be read like Task 5's coefficients.

## Markdown answer cell

```markdown
## Exercise 5 answers
- **Data:** Task 5's split (712 / 179, stratified) and cleaning (median + scale, most frequent + one-hot) → 10 float32 columns. Targets are 0.0 / 1.0 floats, shape `(712, 1)`.
- **Model:** Linear 10 → 16, ReLU, Linear 16 → 1 (a **logit**). `BCEWithLogitsLoss` applies the sigmoid inside; `torch.sigmoid` gives probabilities; ≥ 0.5 means "survived".
- **Result (seed 42):** train accuracy 83.8%, **test 79.3%** (142 of 179). Logistic regression got 80.4% (144) and the tuned forest 79.9% (143): too close to call.
- **Seeds 0–4:** test accuracy from 81.0% to 82.7%, from luck alone. The average of all 6 runs is 81.4%.
- **Lesson:** on small tables, deep learning adds code, settings and seed luck, but no clear accuracy gain. Use logistic regression or trees first.
```

📚 **Learn more:** [`nn.BCEWithLogitsLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html) · [`torch.sigmoid`](https://docs.pytorch.org/docs/stable/generated/torch.sigmoid.html) · [`nn.Sequential`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Sequential.html) · [Reproducibility in PyTorch](https://docs.pytorch.org/docs/stable/notes/randomness.html)

Then commit, push, and ask Claude for **"check, then ex 6"** (save, load and predict, and when deep learning is the right tool).
