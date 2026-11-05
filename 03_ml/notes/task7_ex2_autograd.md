# Task 7, Exercise 2: Autograd, how PyTorch computes gradients (worked example)

Continue in `03_ml/pytorch_basics.ipynb`. Add a Markdown cell `## Exercise 2: Autograd`, then type these cells. The outputs are real (run on 2026-11-05). No new imports.

**The idea in plain words:** training a model means turning its weights a little at a time until the errors are as small as possible. To know *which way* to turn each weight, you need its **gradient**: "if I make this weight a tiny bit bigger, how much does the error change, and in which direction?" A model with 3,649 weights (Exercise 4) needs 3,649 gradients after every batch. **Autograd** (automatic gradients) computes all of them for you with one call: `.backward()`.

## Cell 1: The gradient of x² at 3 is 6

```python
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2
print(y)
y.backward()
print("dy/dx at x = 3:", x.grad)
```
```
tensor(9., grad_fn=<PowBackward0>)
dy/dx at x = 3: tensor(6.)
```
- **`requires_grad=True`** tells PyTorch: "I'll want gradients for this tensor, so record everything you compute from it." `y` shows `grad_fn=<PowBackward0>`: it remembers it came from a power.
- **`y.backward()`** walks that record backwards and stores the gradient of `y` with respect to `x` in **`x.grad`**.
- **The answer is 6**, the slope of the curve y = x² at x = 3. School maths gives the same: the derivative of x² is 2x, and 2 × 3 = 6. PyTorch didn't use that formula; it followed the operations it recorded.
- **`dy/dx`** is the maths notation for "how much y changes per change in x". You'll see it in every tutorial.

## Cell 2: Check it by nudging x

```python
for nudge in [0.1, 0.01, 0.001]:
    growth = ((3 + nudge) ** 2 - 3 ** 2) / nudge
    print(f"x grows by {nudge}: y grows {growth:.3f}× as much")
```
```
x grows by 0.1: y grows 6.100× as much
x grows by 0.01: y grows 6.010× as much
x grows by 0.001: y grows 6.001× as much
```
- **This is what a gradient means:** make x a tiny bit bigger, and y grows about **6 times** that bit. The smaller the nudge, the closer to exactly 6.
- **Why not always compute it this way?** You'd need one extra run of the model per weight. With 7 billion weights (a small LLM), that's 7 billion runs for one step. Autograd gets *all* the gradients from one forward and one backward pass.

## Cell 3: A tiny model, its loss, and 2 gradients

```python
w = torch.tensor(1.0, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)
x_point, y_true = 2.0, 7.0
pred = w * x_point + b
loss = (pred - y_true) ** 2
loss.backward()
print(f"prediction {pred.item()}, loss {loss.item()}")
print(f"dloss/dw = {w.grad.item()}, dloss/db = {b.grad.item()}")
```
```
prediction 2.0, loss 25.0
dloss/dw = -20.0, dloss/db = -10.0
```
- **A one-feature linear model:** `pred = w × x + b`, the same as Task 6's line. With w = 1 and b = 0 it predicts **2**, but the right answer is **7**.
- **The loss is the squared error:** (2 − 7)² = **25**. The **loss** is the one number training tries to make small, like MAE but squared so that the maths works smoothly.
- **Both gradients are negative:** making `w` or `b` bigger makes the loss *smaller*. So training will increase both.
- **`w`'s gradient (−20) is twice `b`'s (−10)** because `w` is multiplied by x = 2: a change in `w` moves the prediction twice as much as the same change in `b`.

## Cell 4: One gradient-descent step by hand

```python
lr = 0.01
with torch.no_grad():
    w -= lr * w.grad
    b -= lr * b.grad
new_loss = (w * x_point + b - y_true) ** 2
print(f"w = {w.item():.2f}, b = {b.item():.2f}")
print(f"loss {loss.item():.2f} → {new_loss.item():.2f}")
```
```
w = 1.20, b = 0.10
loss 25.00 → 20.25
```
- **Gradient descent:** move each weight a small step *against* its gradient: `w = w − lr × gradient`. A negative gradient (−20) makes `w` grow: 1 − 0.01 × (−20) = **1.2**.
- **`lr` is the learning rate**, the size of the step. Cell 6 shows what happens when it's too small or too big.
- **The loss fell from 25 to 20.25** after one step. Training is this step repeated thousands of times, on real data.
- **`with torch.no_grad():`** switches off the recording. The update itself isn't part of the model, so PyTorch must not record it (it would even raise an error without this). You'll also use `no_grad` for predictions, where you don't need gradients.
- **"Descent" because the loss is like a hill.** The gradient points uphill, so you step the opposite way, downhill, towards the lowest loss.

## Cell 5: Gradients add up, so reset them

```python
x = torch.tensor(3.0, requires_grad=True)
for _ in range(3):
    (x ** 2).backward()
    print("x.grad:", x.grad.item())
x.grad.zero_()
print("after zero_():", x.grad.item())
```
```
x.grad: 6.0
x.grad: 12.0
x.grad: 18.0
after zero_(): 0.0
```
- **`backward()` adds to `.grad`; it doesn't replace it.** After 3 calls the gradient is 6 + 6 + 6 = 18, which is wrong for a single step.
- **`x.grad.zero_()`** resets it to 0. The `_` at the end is PyTorch's sign for "changes the tensor in place".
- **That's why every training loop resets the gradients** once per step: by hand in Exercise 3, and with `optimizer.zero_grad()` in Exercise 4. Forgetting it is a classic bug: the model trains, but badly.
- **Why does PyTorch add them up?** Sometimes you *want* to collect gradients over several small batches before one update (when a big batch doesn't fit in memory). Adding up makes that possible.

## Cell 6: The learning rate decides everything

```python
for lr in [0.01, 0.1, 1.1]:
    x = torch.tensor(3.0, requires_grad=True)
    for _ in range(10):
        loss = x ** 2
        loss.backward()
        with torch.no_grad():
            x -= lr * x.grad
        x.grad.zero_()
    print(f"lr {lr}: x after 10 steps = {x.item():.3f}")
```
```
lr 0.01: x after 10 steps = 2.451
lr 0.1: x after 10 steps = 0.322
lr 1.1: x after 10 steps = 18.575
```
- **The goal:** find the x where x² is smallest. The answer is 0; let gradient descent find it, starting at 3.
- **`lr` 0.01 is too small:** after 10 steps x is still 2.45. It would get there, but it would take hundreds of steps.
- **`lr` 0.1 works:** each step multiplies x by 0.8, so it reaches 0.32 after 10 steps.
- **`lr` 1.1 is too big:** each step jumps over the minimum and lands further away on the other side, and x grows to **18.6**. This is called **diverging**. In real training it shows up as a loss that grows, or becomes `nan` (not a number).
- **This inner loop is a complete training loop:** forward (`x ** 2`) → loss → `backward()` → update → reset. Exercise 3 uses the same 5 steps on 43,152 real diamonds.

## Markdown answer cell

```markdown
## Exercise 2 answers
- **Gradient** = how much the output changes when you nudge an input a tiny bit, and in which direction. The gradient of x² at x = 3 is **6** (nudging by 0.001 gives 6.001).
- **Autograd:** `requires_grad=True` records the operations (`grad_fn`), `.backward()` fills `.grad` for every tensor that needs it, from one backward pass.
- **Tiny model:** w = 1, b = 0 predicts 2 for a target of 7, so the loss is 25. Gradients −20 (w) and −10 (b): increase both.
- **Gradient descent:** `w -= lr * w.grad` inside `torch.no_grad()`. One step with lr 0.01: w 1 → 1.2, b 0 → 0.1, loss 25 → 20.25.
- **Gradients add up**, so reset them every step (`.grad.zero_()`).
- **Learning rate:** 0.01 is too slow (2.451), 0.1 works (0.322), 1.1 diverges (18.575).
```

📚 **Learn more:** [Autograd tutorial](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html) · [`Tensor.backward`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.backward.html) · [`torch.no_grad`](https://docs.pytorch.org/docs/stable/generated/torch.no_grad.html) · [Google ML Crash Course: gradient descent](https://developers.google.com/machine-learning/crash-course/linear-regression/gradient-descent)

Then commit, push, and ask Claude for **"check, then ex 3"** (a training loop by hand, on real diamonds).
