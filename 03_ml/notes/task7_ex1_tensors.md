# Task 7, Exercise 1: Tensors (worked example)

**Make a new notebook** `03_ml/pytorch_basics.ipynb`: Ctrl+Shift+P → "Create: New Jupyter Notebook", save it in `03_ml/`, and pick the **dsllm** kernel. Add a Markdown cell `# Task 7: Deep learning basics with PyTorch`, then `## Exercise 1: Tensors`. The outputs below are real (run on 2026-11-05, PyTorch 2.15 on the CPU).

**What's new:** scikit-learn gave you finished models with `fit()`. **PyTorch** gives you the parts to build your own: tensors, gradients, layers and optimizers. It's the library behind most modern AI. Llama, Stable Diffusion and the Hugging Face `transformers` library are all written in PyTorch. Laravel analogy: scikit-learn is like a full package such as Laravel Cashier (call one method and it works), and PyTorch is like the framework itself, where you write the controller logic yourself.

## Cell 1: Imports

```python
import numpy as np
import torch
```
- **It's installed as `torch` and imported as `torch`.** The name comes from Torch, an older library written in the Lua language. This is the **CPU** version, because this PC has no usable graphics card (GPU).
- **The first `import torch` can take a minute** in a new environment (Windows Defender scans the new files). After that it takes a few seconds.
- Later exercises add more imports. **Add them to this cell**, then press **Shift+Alt+O** to sort them.

## Cell 2: Your first tensor

```python
print("PyTorch", torch.__version__)
t = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
print(t)
print("shape:", t.shape, " dims:", t.ndim, " dtype:", t.dtype)
print("whole numbers:", torch.tensor([1, 2, 3]).dtype)
```
```
PyTorch 2.15.0+cpu
tensor([[1., 2., 3.],
        [4., 5., 6.]])
shape: torch.Size([2, 3])  dims: 2  dtype: torch.float32
whole numbers: torch.int64
```
- **A tensor is PyTorch's array.** Like a NumPy array (Task 4), it holds numbers of one type in a grid of any number of dimensions: 1 dimension is a list (a **vector**), 2 is a table (a **matrix**), 3 or more is a stack of tables (a batch of colour images is 4-D: images × colours × height × width).
- **`shape` is `torch.Size([2, 3])`**: 2 rows and 3 columns. `torch.Size` behaves like a tuple, so `t.shape[1]` is 3.
- **`torch.float32` is the default for decimals**, while NumPy uses `float64`. Neural networks don't need 16 digits of precision: 32-bit numbers use half the memory and run faster. Whole numbers become `int64`.
- **`2.15.0+cpu`** is the version on this PC. On another computer or another version, the training numbers in Exercises 3–6 may differ slightly in the last digits.

## Cell 3: From NumPy and back

```python
prices = np.array([326.0, 2401.0, 18823.0])
p = torch.tensor(prices, dtype=torch.float32)
print(prices.dtype, "→", p.dtype)
print(p)
print(p.numpy(), type(p.numpy()))
```
```
float64 → torch.float32
tensor([  326.,  2401., 18823.])
[  326.  2401. 18823.] <class 'numpy.ndarray'>
```
- **`torch.tensor(array, dtype=torch.float32)`** copies a NumPy array (or a list) into a new tensor and converts it to `float32` on the way. You'll use exactly this to feed pandas and scikit-learn data to PyTorch.
- **`.numpy()` goes back** to a NumPy array, for example to use `mean_absolute_error` or matplotlib.
- **`torch.from_numpy(prices)` also exists.** It doesn't copy: the tensor and the array share the same memory, so changing one changes the other, and it keeps NumPy's `float64`. `torch.tensor(...)` is the safer default.

## Cell 4: Maths works like NumPy

```python
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([10.0, 20.0, 30.0])
print(a + b, a * b, a ** 2)
print(a.sum(), a.mean(), a.mean().item())
```
```
tensor([11., 22., 33.]) tensor([10., 40., 90.]) tensor([1., 4., 9.])
tensor(6.) tensor(2.) 2.0
```
- **`+`, `*` and `**` work element by element**, exactly as in NumPy: 1 + 10, 2 + 20, 3 + 30. There's no loop to write.
- **`a.sum()` returns a tensor, not a Python number:** `tensor(6.)` is a 0-dimensional tensor (a **scalar**). **`.item()`** turns a one-number tensor into a plain Python `float`. You'll use it to print losses in the training loops.
- **Most NumPy names exist in PyTorch:** `sum`, `mean`, `exp`, `log`, `reshape`, `arange`. One difference is that NumPy says `axis=` and PyTorch says `dim=` (Cell 7).

## Cell 5: Matrix multiply: a linear model in one line

```python
X = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])  # 2 rows, 3 features
w = torch.tensor([[0.5], [-1.0], [2.0]])  # 1 weight per feature
bias = torch.tensor([1.0])
out = X @ w + bias
print(out)
print(X.shape, "@", w.shape, "→", out.shape)
```
```
tensor([[ 5.5000],
        [10.0000]])
torch.Size([2, 3]) @ torch.Size([3, 1]) → torch.Size([2, 1])
```
- **`@` is matrix multiplication.** For each row it multiplies every feature by its weight and adds them up. Row 1: 1 × 0.5 + 2 × (−1) + 3 × 2 + 1 = **5.5**. Row 2: 4 × 0.5 + 5 × (−1) + 6 × 2 + 1 = **10**.
- **That's a linear model:** the same weighted sum as `LinearRegression.predict` (Task 6), done for all rows at once. A neural network layer (`nn.Linear`, Exercise 4) is exactly `X @ w + bias`.
- **The shape rule:** `(2, 3) @ (3, 1) → (2, 1)`. The inner numbers must match (3 features, 3 weights), and the outer ones give the result: 2 rows, 1 prediction each.
- **`+ bias` adds 1 to every row** even though `bias` has only one number. That's **broadcasting** (Cell 7).

## Cell 6: The 2 most common errors

```python
try:
    X @ torch.tensor([[1.0], [2.0]])
except RuntimeError as error:
    print("Shape error:", error)
try:
    X @ torch.tensor([[1.0], [2.0], [3.0]], dtype=torch.float64)
except RuntimeError as error:
    print("Type error:", error)
```
```
Shape error: mm: mat1 and mat2 shapes cannot be multiplied (2x3 and 2x1)
Type error: expected m1 and m2 to have the same dtype, but got: float != double
```
- **Shape error:** 3 features but only 2 weights. `(2x3 and 2x1)` tells you both shapes. When you see it, print the `.shape` of both sides.
- **Type error:** `float` means `float32` and `double` means `float64`. PyTorch won't mix them. This is the error you get when you forget `dtype=torch.float32` on data that came from NumPy or pandas, because your model's weights are `float32`.
- **Read these two messages now**, so you recognise them later. They are the two errors almost every PyTorch beginner meets in the first week.

## Cell 7: Broadcasting

```python
print(X.mean(dim=0))
print(X - X.mean(dim=0))
print(X * torch.tensor([1.0, 10.0, 100.0]))
```
```
tensor([2.5000, 3.5000, 4.5000])
tensor([[-1.5000, -1.5000, -1.5000],
        [ 1.5000,  1.5000,  1.5000]])
tensor([[  1.,  20., 300.],
        [  4.,  50., 600.]])
```
- **`dim=0` means "go down the rows"**, so you get one mean per column: (1 + 4) / 2 = 2.5, and so on. It's NumPy's `axis=0` with a different name.
- **`X - X.mean(dim=0)`** subtracts a 3-number row from a 2 × 3 table. PyTorch **broadcasts**: it repeats the row for every row of `X`. That's the first half of what `StandardScaler` does (subtract the mean, then divide by the standard deviation).
- **`X * torch.tensor([1.0, 10.0, 100.0])`** scales each column by its own number. The rule is the same as NumPy's: shapes are compared from the right, and a size of 1 (or a missing dimension) is stretched to fit.

## Cell 8: Reshaping, and a silent bug

```python
y = torch.arange(6.0)
print(y, y.shape)
print(y.reshape(2, 3))
col = y.reshape(-1, 1)
print(col.shape, col.squeeze(1).shape, X.T.shape)
print("(6, 1) minus (6,) gives", (col - y).shape)
```
```
tensor([0., 1., 2., 3., 4., 5.]) torch.Size([6])
tensor([[0., 1., 2.],
        [3., 4., 5.]])
torch.Size([6, 1]) torch.Size([6]) torch.Size([3, 2])
(6, 1) minus (6,) gives torch.Size([6, 6])
```
- **`reshape(2, 3)`** puts the same 6 numbers into 2 rows of 3. The total must stay the same.
- **`reshape(-1, 1)`** means "1 column, and work out the number of rows yourself" (here 6). A model returns one column of predictions, shape `(rows, 1)`, so your targets should have that shape too.
- **`squeeze(1)`** removes a dimension of size 1: `(6, 1)` → `(6,)`. **`.T`** swaps rows and columns: `(2, 3)` → `(3, 2)`.
- **The silent bug:** `(6, 1) − (6,)` broadcasts to **`(6, 6)`**: every prediction minus every target, 36 numbers instead of 6. There's no error, and the loss is simply wrong. That's why Exercises 3–5 always `reshape(-1, 1)` the targets.

## Cell 9: Why not just NumPy?

```python
print("GPU available:", torch.cuda.is_available())
print("t lives on:", t.device)
k = torch.tensor(2.0, requires_grad=True)
print(k * 3)
```
```
GPU available: False
t lives on: cpu
tensor(6., grad_fn=<MulBackward0>)
```
- **Superpower 1: GPUs.** A tensor lives on a **device**. Here it's the CPU, because this PC has no GPU. On a computer with an NVIDIA card, `t.to("cuda")` moves it to the GPU, and the same code runs 10–100× faster on big models. NumPy only runs on the CPU.
- **Superpower 2: gradients.** With `requires_grad=True`, PyTorch remembers *how* each result was computed. `grad_fn=<MulBackward0>` means "this came from a multiplication". From that record, it can work out how to change `k` to change the result. That's how every neural network learns, and it's Exercise 2.
- **Training big models needs both:** billions of multiplications (GPUs make them fast) and a gradient for every weight (autograd computes them for you).

## Markdown answer cell

```markdown
## Exercise 1 answers
- **Tensor** = PyTorch's array: `shape`, `ndim`, `dtype`. Decimals default to **float32** (NumPy uses float64): half the memory and precise enough for neural networks.
- **NumPy ↔ PyTorch:** `torch.tensor(array, dtype=torch.float32)` copies in, `.numpy()` goes back. `.item()` turns a one-number tensor into a Python float.
- **`X @ w + bias`** is a linear model for every row at once. Shape rule: `(2, 3) @ (3, 1) → (2, 1)`.
- **2 common errors:** shapes that don't match (`2x3 and 2x1`), and mixing float32 with float64 (`float != double`).
- **Broadcasting** repeats a smaller tensor to fit (`X - X.mean(dim=0)`). Danger: `(6, 1) − (6,)` silently becomes `(6, 6)`, so keep targets as `(rows, 1)`.
- **Why tensors exist:** they run on GPUs, and they record how they were computed so PyTorch can compute gradients (`grad_fn`).
```

📚 **Learn more:** [Tensors tutorial](https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html) · [`torch.tensor`](https://docs.pytorch.org/docs/stable/generated/torch.tensor.html) · [Broadcasting semantics](https://docs.pytorch.org/docs/stable/notes/broadcasting.html) · [`Tensor.reshape`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.reshape.html)

Then commit, push, and ask Claude for **"check, then ex 2"** (autograd: how PyTorch computes gradients).
