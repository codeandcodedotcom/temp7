# ---------------- CONFIG ----------------
catalog = "dsenprd"
schema = "lit_prepare"
src_table = f"{catalog}.{schema}.prepare_historical_data"
out_table = f"{catalog}.{schema}.embedding_prepare_historical_data"
model_name = "sister_v2_small"
BATCH_SIZE = 200   # safe for 419 rows; lower if you hit timeouts
# ----------------------------------------

from databricks import generative_ai as ai
import pandas as pd
from datetime import datetime

# 1) Load source into pandas (safe for 419 rows)
pdf = spark.read.table(src_table).select("id", "Finding", "Action").toPandas()

# 2) Prepare text lists (preserve order)
findings = pdf["Finding"].fillna("").astype(str).tolist()
actions  = pdf["Action"].fillna("").astype(str).tolist()

# 3) embedding helper (batched)
embedder = ai.Embeddings(model=model_name)

def batch_embed(texts, batch_size=BATCH_SIZE):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # single API call per batch
        batch_embs = embedder.embed(batch)
        embeddings.extend([[float(x) for x in v] for v in batch_embs])
    return embeddings

# 4) Get embeddings (two separate lists)
finding_embs = batch_embed(findings)
action_embs  = batch_embed(actions)

# 5) Attach embeddings to pandas dataframe
pdf["finding_embedding"] = finding_embs
pdf["action_embedding"]  = action_embs
pdf["ingestion_ts"] = datetime.utcnow()

# 6) Convert back to Spark and write as Delta table in Unity Catalog
sdf = spark.createDataFrame(pdf)   # Infers ArrayType for embedding lists
sdf.write.mode("overwrite").saveAsTable(out_table)

print("Wrote", len(pdf), "rows to", out_table)
display(sdf.limit(10))
