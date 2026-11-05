# Task 7, Exercise 6: Save, load, predict, and when to use deep learning (worked example)

Continue in `03_ml/pytorch_basics.ipynb`. Add a Markdown cell `## Exercise 6: Save, load, predict, and when to use deep learning`, then type these cells. The outputs are real (run on 2026-11-05). The predicted prices may differ by a few dollars on another computer or PyTorch version.

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
import joblib
```
After this exercise, your whole imports cell should look like this:
```python
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
```

## Cell 1: What's inside a model, and saving it

```python
models_dir = Path("models")
models_dir.mkdir(exist_ok=True)
for name, weights in price_net.state_dict().items():
    print(f"{name:17} {tuple(weights.shape)}")
net_path = models_dir / "diamond_price_net.pt"
prep_path = models_dir / "diamond_price_net_prep.joblib"
torch.save(price_net.state_dict(), net_path)
joblib.dump(diamond_prep, prep_path)
for path in [net_path, prep_path]:
    print(f"Saved {path.name} ({path.stat().st_size / 1024:.0f} KB)")
```
```
layers.0.weight   (64, 23)
layers.0.bias     (64,)
layers.2.weight   (32, 64)
layers.2.bias     (32,)
layers.4.weight   (1, 32)
layers.4.bias     (1,)
Saved diamond_price_net.pt (17 KB)
Saved diamond_price_net_prep.joblib (4 KB)
```
- **`state_dict()`** is a dict of every weight tensor, by name. `layers.0` is the first `nn.Linear`: 64 × 23 weights (PyTorch stores them as outputs × inputs) + 64 biases. `layers.1` and `layers.3` are the ReLUs, which have no weights, so they're missing.
- **`torch.save(state_dict, path)`** writes the weights to a `.pt` file. It's tiny (17 KB) because 3,649 numbers × 4 bytes is only 14.6 KB. Compare Task 6's boosting file: 566 KB.
- **Save the weights, not the whole model object.** The `.pt` file holds only numbers, not the `PriceNet` class. Laravel analogy: it's a database dump without the migrations. To load it, you need the same table structure, which here is the same class with the same layer sizes.
- **The `.pt` file is only half the model.** The network expects 23 *scaled, one-hot* columns, so the `ColumnTransformer` that makes them must be saved too (with `joblib`, as in Task 5). Lose it, and the weights are useless. In Phase 4, your API loads both files.

## Cell 2: Load into a fresh model

```python
loaded_net = PriceNet(n_features=23)
print(loaded_net.load_state_dict(torch.load(net_path, weights_only=True)))
loaded_net.eval()
loaded_prep = joblib.load(prep_path)
```
```
<All keys matched successfully>
```
- **First build an empty `PriceNet`** with the same sizes (random weights), then pour the saved weights in. `<All keys matched successfully>` means every name and shape fitted.
- **`weights_only=True`** tells `torch.load` to accept only tensors and simple types. A `.pt` file can contain pickled Python objects, and loading a pickle can run code (the same trust rule as `joblib.load` in Task 5). It's the default since PyTorch 2.6; writing it makes the intent clear.
- **`loaded_net.eval()`** before predicting, every time. It switches off training-only behaviour (such as dropout) in models that have it.

## Cell 3: Price the 3 diamonds from Task 6

```python
new_diamonds = pd.DataFrame([
    {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
     "depth": 61.5, "table": 56.0},
    {"carat": 1.0, "cut": "Premium", "color": "G", "clarity": "SI1",
     "depth": 62.0, "table": 58.0},
    {"carat": 2.0, "cut": "Good", "color": "J", "clarity": "I1",
     "depth": 63.0, "table": 59.0},
])
new_t = to_tensor(loaded_prep.transform(new_diamonds))
with torch.no_grad():
    log_prices = loaded_net(new_t)
    print("Same as before saving:", torch.equal(log_prices, price_net(new_t)))
boosting = joblib.load(models_dir / "diamond_price_model.joblib")
display(new_diamonds.assign(
    neural_net=torch.exp(log_prices).squeeze(1).numpy().round(0),
    boosting=boosting.predict(new_diamonds).round(0),
))
```
```
Same as before saving: True
   carat      cut color clarity  depth  table  neural_net  boosting
0    0.5    Ideal     E     VS1   61.5   56.0      1687.0    1773.0
1    1.0  Premium     G     SI1   62.0   58.0      4638.0    4588.0
2    2.0     Good     J      I1   63.0   59.0      6079.0    6713.0
```
- **The prediction path:** raw rows → saved `ColumnTransformer` → tensor → network → `exp` → dollars. A `/predict` endpoint does exactly this for each request.
- **`torch.equal`** checks that every number is identical: the loaded network *is* the trained one.
- **The 2 models agree within 1–9%**, although one is a neural network and the other is hundreds of trees. Both learned the same patterns from the same diamonds.
- **The biggest gap is the 2-carat J I1 diamond** ($6,079 vs $6,713). Only 8 of the 53,940 diamonds weigh 1.8–2.2 carats with J colour and I1 clarity (there are 417 near 0.5 carat E VS1), so both models have to guess more there. Boosting is the better model overall ($285 vs $336 MAE), so trust it more.
- **`torch.no_grad()`** for predictions: no recording, less memory, faster. Without it, the outputs would carry a `grad_fn`, and `.numpy()` would raise an error.

## Cell 4: How big are real deep-learning models?

```python
block = nn.TransformerEncoderLayer(d_model=768, nhead=12, dim_feedforward=3072)
tokens = nn.Embedding(50257, 768)
positions = nn.Embedding(1024, 768)
final_norm = nn.LayerNorm(768)
gpt2_small = (count_params(tokens) + count_params(positions)
              + 12 * count_params(block) + count_params(final_norm))
print(f"PriceNet:              {count_params(price_net):>11,} parameters")
print(f"One transformer block: {count_params(block):>11,} parameters")
print(f"GPT-2 small:           {gpt2_small:>11,} parameters, "
      f"{gpt2_small * 4 / 1e6:,.0f} MB as float32")
```
```
PriceNet:                    3,649 parameters
One transformer block:   7,087,872 parameters
GPT-2 small:           124,439,808 parameters, 498 MB as float32
```
- **An LLM is a huge `nn.Module`**, built from the same parts you used: `nn.Linear` layers, an activation, an optimizer, `backward()`, and a `state_dict` saved to disk. The new parts are an **embedding** (one learned vector of 768 numbers per word piece, or **token**) and **attention** (each token looks at the tokens before it).
- **This is the size of GPT-2 small** (OpenAI, 2019): 50,257 tokens × 768, 1,024 positions, and 12 transformer blocks. GPT-2 blocks also hide the later words from each word, but that mask adds no weights, so the count is exact: **124,439,808**. The `.pt` file would be about 500 MB.
- **Today's open models are much bigger:** Llama 3 8B has 8 billion parameters, 16 GB in 16-bit numbers. In Phase 5, Ollama runs such models in about 5 GB by storing each weight in about 4 bits ("quantisation"). You won't train an LLM, but now you know what one is: a `state_dict` with billions of numbers, and a `forward` that predicts the next token.

## When is deep learning the right tool?

| Data | Best first choice | Why |
|---|---|---|
| **Tables** (prices, customers, passengers) | gradient boosting or logistic regression | Each column already means something. Trees win, and train in seconds (Exercises 4–5) |
| **Images** (photos, scans, X-rays) | a pretrained network (CNN or vision transformer) | No human can write "features" for pixels; the network learns them |
| **Text** (chat, search, classification) | a pretrained transformer, often an LLM through an API | Meaning depends on word order and context. That's Phase 5 |
| **Audio** (speech to text) | a pretrained network such as Whisper | Raw sound waves, like pixels |
| **Small data** (under about 10,000 rows) | anything but a network trained from scratch | Too little data to learn thousands of weights; fine-tune a pretrained model instead |

- **As an AI engineer you'll rarely train a network from scratch.** You'll load **pretrained** ones (Hugging Face, Ollama, OpenAI) and use them, fine-tune them, or call them from an API. What this task gives you is the vocabulary for that work: tensors, `dtype`, devices, `state_dict`, `eval()`, `no_grad()`, epochs, batches, loss curves and overfitting.
- **Job ads that say "PyTorch"** for LLM roles usually mean exactly that: loading models with `transformers`, running them on a GPU, and fine-tuning. All of it is built on what you did here.

## For comparison only: the Exercise 4 model in Keras (not run, TensorFlow isn't installed)

Some job ads ask for **TensorFlow / Keras**, Google's deep learning library. Here is the same network in Keras 3, so you can recognise it. **This code was not run**, so there is no output. Don't type it into your notebook.

```python
import keras
from keras import layers

keras.utils.set_random_seed(42)
model = keras.Sequential([
    keras.Input(shape=(23,)),
    layers.Dense(64, activation="relu"),
    layers.Dense(32, activation="relu"),
    layers.Dense(1),
])
model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss="mse")
history = model.fit(
    X_fit_t.numpy(), y_fit_t.numpy(),
    validation_data=(X_val_t.numpy(), y_val_t.numpy()),
    batch_size=256, epochs=30,
)
model.save("models/diamond_price_net.keras")
```
- **`layers.Dense`** is Keras's name for `nn.Linear`, and `activation="relu"` puts the ReLU inside the layer.
- **`model.fit()` writes the training loop for you**: batches, shuffling, `zero_grad`, `backward`, `step` and the validation loss per epoch. It's shorter, but you can't change what happens inside each step as easily.
- **The ideas carry over 1-to-1:** layers, activation, optimizer, learning rate, loss, batch size, epochs, validation data. If you know one library, you can read the other in an afternoon. PyTorch is the more common choice today in research and for LLM work.

## Markdown answer cell

```markdown
## Exercise 6 answers
- **Saved:** `price_net.state_dict()` (6 tensors) with `torch.save` → `models/diamond_price_net.pt` (17 KB), plus the `ColumnTransformer` with `joblib` (the network is useless without it).
- **Loaded:** a fresh `PriceNet(23)` + `load_state_dict(torch.load(..., weights_only=True))` → `<All keys matched successfully>`, then `eval()`. Its predictions are identical (`torch.equal`).
- **3 new diamonds:** network **$1,687 / $4,638 / $6,079**; boosting $1,773 / $4,588 / $6,713.
- **Scale:** PriceNet has 3,649 parameters; GPT-2 small has **124,439,808** (about 500 MB). An LLM is a huge `nn.Module` built from the same parts.
- **When to use deep learning:** images, text, audio and very large data sets, usually starting from a pretrained model. For tables, use gradient boosting or logistic regression first.
```

📚 **Learn more:** [Saving and loading models (tutorial)](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html) · [`torch.save`](https://docs.pytorch.org/docs/stable/generated/torch.save.html) · [`torch.load`](https://docs.pytorch.org/docs/stable/generated/torch.load.html) · [`nn.TransformerEncoderLayer`](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html) · [Keras: the Sequential model](https://keras.io/guides/sequential_model/)

## ✅ Task 7 done when
- [ ] All 6 exercises have their cells and an answers cell.
- [ ] **Restart → Run All** runs top to bottom with no errors (about 40 seconds).
- [ ] `output/` has `loss_curve.png`, and `models/` has `diamond_price_net.pt` and `diamond_price_net_prep.joblib`.

Then commit, push, and ask Claude to **"review all"**. That finishes Task 7.
