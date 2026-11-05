# Task 7: Deep learning basics with PyTorch (Phase 3)

**Goal:** learn how a neural network is built and trained, using **PyTorch**. You'll start with tensors and gradients, write a training loop by hand, then train small networks on the diamonds (Task 6) and the Titanic (Task 5), and compare them honestly with the scikit-learn models you already have. The last exercise saves a network, loads it, and shows how the same parts scale up to an LLM.

**Why it matters:** many AI-engineer job ads, including local ones ("AI/ML Engineer, Python/PyTorch"), ask for PyTorch, and the Hugging Face versions of open LLMs (Llama, Mistral, Qwen) are PyTorch `nn.Module`s. In Phase 5 you'll run such models through Ollama and APIs. This task gives you the words and the habits for that work (tensors, `dtype`, devices, `state_dict`, `eval()`, `no_grad()`, epochs, batches, loss curves) and the judgement to know when a neural network is the wrong tool.

**Data:** the same files as before: [data/diamonds.csv](data/diamonds.csv) (Task 6) and [../02_data/data/titanic.csv](../02_data/data/titanic.csv) (Task 5). Exercise 6 also loads Task 6's saved model, `models/diamond_price_model.joblib`, so finish Task 6 Exercise 8 first.

```
03_ml/
├── TASK_7.md
├── pytorch_basics.ipynb   ← Exercises 1–6 (new notebook)
├── notes/                 ← worked examples (task7_ex1_... to task7_ex6_...)
├── examples/              ← task7_pytorch_basics.ipynb, the finished reference notebook
├── output/                ← loss_curve.png, rebuilt by running the notebook
└── models/                ← diamond_price_net.pt + its prep file, rebuilt by running the notebook
```

**Use these settings everywhere,** so your numbers match the expected answers:
- `torch.manual_seed(42)` right before you create random weights or a model, and `generator=torch.Generator().manual_seed(42)` in every `DataLoader` with `shuffle=True`.
- Diamonds: `train_test_split(..., test_size=0.2, random_state=42)` as in Task 6. Titanic: `test_size=0.2, random_state=42, stratify=y` as in Task 5.
- Training numbers may differ slightly in the last digits on another computer or PyTorch version (these were made with PyTorch 2.15 on the CPU). Times depend on your CPU.

**Words you'll meet:**

| Word | Meaning |
|---|---|
| **tensor** | PyTorch's array, like a NumPy array that can also run on a GPU and record how it was computed |
| **gradient** | how much the loss changes when you nudge one weight a tiny bit, and in which direction |
| **autograd** | PyTorch's automatic gradients: `loss.backward()` fills `.grad` for every weight |
| **loss** | one number that measures how wrong the model is (MSE for numbers, cross-entropy for yes/no). Training makes it small |
| **gradient descent** | move every weight a small step against its gradient, again and again |
| **learning rate** | the size of that step (`lr`). Too small = slow, too big = it explodes |
| **layer** | one step of the network, such as `nn.Linear` (a weighted sum) or `nn.ReLU` (negatives → 0) |
| **MLP** | multi-layer perceptron: linear layers with an activation (ReLU) between them; the middle ones are **hidden layers** |
| **optimizer** | the object that updates the weights from their gradients (`Adam`) |
| **batch / epoch** | a batch is a small group of rows used for one update; an epoch is one pass over all the training rows |
| **logit** | a raw score before the sigmoid: positive means "yes", negative means "no" |

---

## Exercise 1: Tensors

1. Create a 2 × 3 tensor from a list of lists. Print it, its `shape`, `ndim` and `dtype`, and the `dtype` of a tensor of whole numbers.
2. Turn a NumPy array of 3 prices into a `float32` tensor, and back with `.numpy()`.
3. Add, multiply and square tensors element by element; print `sum()`, `mean()` and `mean().item()`.
4. Compute `X @ w + bias` for a 2 × 3 `X` and 3 weights. Then trigger (inside `try` / `except RuntimeError`) a shape error and a `float32` vs `float64` error.
5. Use broadcasting: subtract the column means (`dim=0`), and multiply each column by its own number.
6. Reshape `torch.arange(6.0)` to `(2, 3)` and `(-1, 1)`, use `squeeze(1)` and `.T`, and show what shape `(6, 1) − (6,)` gives.
7. Print `torch.cuda.is_available()`, the tensor's `device`, and a tensor made from one with `requires_grad=True`.

✅ Expected: `torch.Size([2, 3])`, `torch.float32` (whole numbers: `torch.int64`). NumPy's `float64` becomes `torch.float32`. `X @ w + bias` gives **5.5** and **10.0**, shape `(2, 1)`. The errors: `mat1 and mat2 shapes cannot be multiplied (2x3 and 2x1)` and `float != double`. Column means `[2.5, 3.5, 4.5]`. `(6, 1) − (6,)` silently becomes **`(6, 6)`**. No GPU, device `cpu`, and `tensor(6., grad_fn=<MulBackward0>)`.

📚 Look up: `torch.tensor`, `Tensor.numpy`, broadcasting semantics, `Tensor.reshape`.

## Exercise 2: Autograd

1. Make `x = 3` with `requires_grad=True`, compute `y = x ** 2`, call `y.backward()` and print `x.grad`. Check it by nudging x by 0.1, 0.01 and 0.001.
2. A tiny model: `pred = w × 2 + b` with w = 1, b = 0 and a target of 7. Print the squared-error loss and the gradients of `w` and `b`.
3. Do one gradient-descent step by hand (`lr = 0.01`) inside `torch.no_grad()` and print the new loss.
4. Call `backward()` 3 times in a row and print `x.grad` each time, then reset it with `zero_()`.
5. Minimise x² from x = 3 for 10 steps with learning rates 0.01, 0.1 and 1.1.

✅ Expected: `x.grad` is **6** (nudging gives 6.100, 6.010, 6.001). The tiny model predicts 2, loss **25**, gradients **−20** (w) and **−10** (b). After one step: w = 1.20, b = 0.10, loss 25 → **20.25**. Gradients add up: 6, 12, 18, then 0. After 10 steps: **2.451** (too slow), **0.322** (good), **18.575** (diverges).

📚 Look up: `requires_grad`, `Tensor.backward`, `torch.no_grad`, gradient descent.

## Exercise 3: A training loop by hand

1. Load the diamonds and split them as in Task 6. Make float32 tensors of shape `(43152, 1)` for log carat and log price of the training set.
2. Fit `LinearRegression` on the same two tensors (as NumPy arrays) and print its slope and intercept.
3. With `torch.manual_seed(42)`, start `w` and `b` from `torch.randn(1, requires_grad=True)`. Train for 300 steps with `lr = 0.1`: forward → MSE loss → `backward()` → update → reset the gradients. Print the loss, `w` and `b` every 50 steps.
4. Compare with scikit-learn, then compute the test MAE in dollars (`torch.exp`) and what twice the carat does to the price.

✅ Expected: the first log carat is 0.6981 and the first log price 9.6947. scikit-learn: slope **1.6780**, intercept **8.4502**. The loop: loss **61.41** at step 0, **0.0692** from step 100; it ends at slope 1.6780 and intercept 8.4502, the same. Test MAE **$839** (Task 6's plain line: $1,010). Twice the carat = **3.2×** the price.

📚 Look up: `torch.manual_seed`, `torch.randn`, the "optimizing model parameters" tutorial.

## Exercise 4: A neural network with nn.Module, an optimizer and mini-batches

1. Split the training diamonds again (80/20, `random_state=42`) into fit and validation sets. Build a `ColumnTransformer`: log then scale `carat`, scale `depth` and `table`, `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` for the grades. Turn the fit, validation and test sets into float32 tensors, and the log prices into `(rows, 1)` tensors.
2. Write `class PriceNet(nn.Module)`: Linear 23 → 64, ReLU, Linear 64 → 32, ReLU, Linear 32 → 1. Print it and count its parameters.
3. Wrap the fit tensors in a `TensorDataset` and a `DataLoader` (batches of 256, shuffled, seeded). Look at one batch.
4. Train for 30 epochs with `torch.optim.Adam(lr=0.001)` and `nn.MSELoss()`. After each epoch, record the train loss and the validation loss. Time it.
5. Draw both loss curves (log y-axis), save the chart as `output/loss_curve.png`, and look at it.
6. Compute the test MAE in dollars and compare it with Task 6.

✅ Expected: fit `(34521, 23)`, validation `(8631, 23)`, test `(10788, 23)`. **3,649** parameters; 135 batches per epoch. Losses: epoch 1 train 19.40 / validation 0.248, epoch 30 train **0.0128** / validation **0.0134**, in about 10 s. The two curves stay close: no overfitting. Test MAE **$336**: better than linear on log scales ($400), worse than tuned gradient boosting (**$285**). On tables, boosting usually wins.

📚 Look up: `nn.Module`, `nn.Linear`, `nn.ReLU`, `nn.Sequential`, `TensorDataset`, `DataLoader`, `torch.optim.Adam`, `nn.MSELoss`.

## Exercise 5: Classification: Titanic survival with a neural network

1. Load the raw Titanic data and split it as in Task 5. Use Task 5's cleaning (median + scale for numbers, most frequent + one-hot for text, with `sparse_output=False`), and make float32 tensors; the targets are 0.0 / 1.0 with shape `(rows, 1)`.
2. Print `torch.sigmoid` of the logits −3, 0 and 2, and the predictions with a 0.5 cut-off.
3. Write `accuracy(net, X_t, y_t)` and `train_survival_net(seed, epochs=50, verbose=False)`: Linear 10 → 16, ReLU, Linear 16 → 1, `nn.BCEWithLogitsLoss()`, Adam (lr 0.001), batches of 32. Train it with seed 42 and print the train loss and accuracy every 10 epochs.
4. Score the test set once: the first 5 survival chances, and the accuracy.
5. Train again with seeds 0–4 and show the train and test accuracy for each.

✅ Expected: train `(712, 10)`, test `(179, 10)`; survival rate 38.3% / 38.5%. Sigmoid: **0.0474, 0.5, 0.8808** → `[0, 1, 1]`. Seed 42: train accuracy 83.8%, first 5 chances `[0.09 0.09 0.19 0.05 0.68]`, test **79.3%** (142 of 179). Seeds 0–4: test **81.0% to 82.7%**. Logistic regression got 80.4% and the tuned forest 79.9% in Task 5, so the network is no clear win: on small tables, deep learning isn't needed.

📚 Look up: `nn.BCEWithLogitsLoss`, `torch.sigmoid`, logits, reproducibility in PyTorch.

## Exercise 6: Save, load, predict, and when to use deep learning

1. Print the names and shapes in `price_net.state_dict()`. Save it with `torch.save` to `models/diamond_price_net.pt`, and save the `ColumnTransformer` with `joblib` to `models/diamond_price_net_prep.joblib`. Print both file sizes.
2. Build a fresh `PriceNet(n_features=23)`, load the weights with `torch.load(..., weights_only=True)`, call `eval()`, and load the prep file.
3. Price Task 6's 3 new diamonds with the loaded network (inside `torch.no_grad()`), check they equal the original network's predictions, and put them next to Task 6's boosting model.
4. Count the parameters of one `nn.TransformerEncoderLayer(d_model=768, nhead=12, dim_feedforward=3072)` and of a GPT-2-small-sized model (2 embeddings, 12 blocks, a final `LayerNorm`).
5. Read the "when is deep learning the right tool?" table and the Keras version of Exercise 4's model in the notes (for comparison only, not run).

✅ Expected: 6 tensors (`layers.0.weight` is `(64, 23)`); the `.pt` file is **17 KB** and the prep file 4 KB. `<All keys matched successfully>`, and `Same as before saving: True`. Network: **$1,687 / $4,638 / $6,079**; boosting: $1,773 / $4,588 / $6,713. One transformer block: **7,087,872** parameters; GPT-2 small: **124,439,808** (about 500 MB as float32).

📚 Look up: `state_dict`, `torch.save`, `torch.load(weights_only=True)`, `nn.TransformerEncoderLayer`, `nn.Embedding`, Keras `Sequential`.

---

## How to work
1. Make a new notebook, `03_ml/pytorch_basics.ipynb`. Do the exercises in order, and commit after each one.
2. The worked examples are in [notes/](notes/) (`task7_ex1_...` to `task7_ex6_...`). The finished notebook, with every output, is [examples/task7_pytorch_basics.ipynb](examples/task7_pytorch_basics.ipynb). Type your own version first; use it only to compare or to get unstuck.
3. When you're done, ask Claude to **"review all"**.
