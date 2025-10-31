import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import os

# ========= CONFIG =========
MODEL_NAME = "hyp1231/blair-roberta-base"  # same as official repo
INPUT_FILE = "/scratch/sshar386/amazon_data/products.parquet"
OUTPUT_FILE = "/scratch/sshar386/amazon_data/product_embeddings.parquet"
OUTPUT_NPY = "/scratch/sshar386/amazon_data/product_embeddings.npy"
BATCH_SIZE = 32
MAX_LENGTH = 512

# ========= SETUP =========
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"✅ Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

# ========= LOAD DATA =========
df = pd.read_parquet(INPUT_FILE)
text_cols = [c for c in ["title", "description", "features"] if c in df.columns]
df[text_cols] = df[text_cols].fillna("")
df["combined_text"] = df[text_cols].agg(" ".join, axis=1)

texts = df["combined_text"].tolist()
product_ids = df["parent_asin"].tolist()

# ========= EMBEDDING LOOP =========
all_embs = []
for i in tqdm(range(0, len(texts), BATCH_SIZE)):
    batch_texts = texts[i:i + BATCH_SIZE]
    inputs = tokenizer(batch_texts,
                       padding=True,
                       truncation=True,
                       max_length=MAX_LENGTH,
                       return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        # CLS pooling (matches generate_emb.py)
        cls_emb = outputs.last_hidden_state[:, 0, :].detach().cpu().numpy()
        all_embs.append(cls_emb)

embeddings = np.concatenate(all_embs, axis=0)
print(f"✅ Embeddings shape: {embeddings.shape}")

# ========= SAVE OUTPUT =========
out_df = pd.DataFrame({
    "parent_asin": product_ids,
    "embedding": [emb.tolist() for emb in embeddings]
})
pq.write_table(pa.Table.from_pandas(out_df), OUTPUT_FILE, compression="snappy")
print(f"✅ Saved {len(out_df)} embeddings to {OUTPUT_FILE}")

# ========= SAVE AS .NPY TOO =========
np.save(OUTPUT_NPY, embeddings)
print(f"✅ Also saved raw NumPy array to {OUTPUT_NPY}")
