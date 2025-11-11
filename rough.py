# ---------------- CONFIG ----------------
catalog = "dsenprd"
schema = "lit_prepare"

src_table = f"{catalog}.{schema}.prepare_historical_data"
out_table = f"{catalog}.{schema}.embedding_prepare_historical_data"

BATCH_SIZE = 200
# ----------------------------------------

from databricks_langchain import DatabricksEmbeddings
import pandas as pd
import numpy as np
import json
from datetime import datetime

embedder = DatabricksEmbeddings(endpoint="sister_v2_small")

# 1️⃣ Load data (test small subset first)
pdf = (
    spark.read.table(src_table)
    .select("id", "Finding", "Action")
    # .limit(10)    # 👈 uncomment for testing
    .toPandas()
)

# 2️⃣ Batch embedding helper
def batch_embed(texts, batch_size=BATCH_SIZE):
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        results = [embedder.embed_query(t) for t in batch]
        all_embs.extend(results)
    return all_embs

findings = pdf["Finding"].fillna("").astype(str).tolist()
actions  = pdf["Action"].fillna("").astype(str).tolist()

finding_embs = batch_embed(findings)
action_embs  = batch_embed(actions)

# 3️⃣ Convert numpy arrays → Python lists, then → JSON strings
def emb_to_json(v):
    if v is None:
        return json.dumps([])
    if isinstance(v, np.ndarray):
        v = v.tolist()
    return json.dumps([float(x) for x in v])

pdf["finding_embedding"] = [emb_to_json(v) for v in finding_embs]
pdf["action_embedding"]  = [emb_to_json(v) for v in action_embs]
pdf["ingestion_ts"] = datetime.utcnow()

# 4️⃣ Convert to Spark DataFrame safely (all columns are string/primitive)
sdf = spark.createDataFrame(pdf)

# 5️⃣ Save table
sdf.write.mode("overwrite").saveAsTable(out_table)

print(f"✅ Embedded {len(pdf)} rows and saved successfully to {out_table}")
display(spark.read.table(out_table).limit(10))
