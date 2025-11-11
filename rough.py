# ---------------- CONFIG ----------------
catalog = "dsenprd"
schema = "lit_prepare"

src_table = f"{catalog}.{schema}.prepare_historical_data"
out_table = f"{catalog}.{schema}.embedding_prepare_historical_data"

BATCH_SIZE = 200     # number of rows per embedding batch
# ----------------------------------------

from databricks_langchain import DatabricksEmbeddings
import pandas as pd
import numpy as np
from datetime import datetime

# Initialize embedding model (inside Databricks workspace)
embedder = DatabricksEmbeddings(endpoint="sister_v2_small")

# 1️⃣ Load data (use limit(10) for quick test first)
pdf = (
    spark.read.table(src_table)
    .select("id", "Finding", "Action")
    # .limit(10)   # 👈 uncomment for test run
    .toPandas()
)

# 2️⃣ Helper to clean + batch embed texts
def batch_embed(texts, batch_size=BATCH_SIZE):
    """Embed text list in small batches."""
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # model expects simple strings
        results = [embedder.embed_query(t) for t in batch]
        embeddings.extend(results)
    return embeddings

# 3️⃣ Prepare clean text lists
findings = pdf["Finding"].fillna("").astype(str).tolist()
actions  = pdf["Action"].fillna("").astype(str).tolist()

# 4️⃣ Embed both columns
finding_embs = batch_embed(findings)
action_embs  = batch_embed(actions)

# 5️⃣ Convert numpy arrays → Python lists of floats
def to_list(v):
    if v is None:
        return []
    if isinstance(v, np.ndarray):
        return v.astype(float).tolist()
    if isinstance(v, (list, tuple)):
        return [float(x) for x in v]
    return [float(v)]

pdf["finding_embedding"] = [to_list(v) for v in finding_embs]
pdf["action_embedding"]  = [to_list(v) for v in action_embs]
pdf["ingestion_ts"] = datetime.utcnow()

# 6️⃣ Convert to Spark DataFrame and save as Delta table
sdf = spark.createDataFrame(pdf)
sdf.write.mode("overwrite").saveAsTable(out_table)

# 7️⃣ Verify output
print(f"✅ Embedded {len(pdf)} rows and saved to {out_table}")
display(spark.read.table(out_table).limit(10))
