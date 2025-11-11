# ---------------- CONFIG ----------------
catalog = "dsenprd"
schema = "lit_prepare"
src_table = f"{catalog}.{schema}.prepare_historical_data"
out_table = f"{catalog}.{schema}.embedding_prepare_historical_data"
BATCH_SIZE = 200
# ----------------------------------------

from databricks_langchain import DatabricksEmbeddings
import pandas as pd
from datetime import datetime

# init model client (works inside Databricks workspace)
embedder = DatabricksEmbeddings(endpoint="sister_v2_small")

# 1) Load a small subset first to test
pdf = (
    spark.read.table(src_table)
    .select("id", "Finding", "Action")
    .limit(10)     # 👈 test first; remove after verifying
    .toPandas()
)

# 2) Prepare text lists
findings = pdf["Finding"].fillna("").astype(str).tolist()
actions  = pdf["Action"].fillna("").astype(str).tolist()

# 3) Helper for batched embedding
def batch_embed(texts, batch_size=BATCH_SIZE):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embs = [embedder.embed_query(t) for t in batch]  # one call per text
        embeddings.extend(batch_embs)
    return embeddings

# 4) Get embeddings
finding_embs = batch_embed(findings)
action_embs  = batch_embed(actions)

# 5) Add to DataFrame
pdf["finding_embedding"] = finding_embs
pdf["action_embedding"]  = action_embs
pdf["ingestion_ts"] = datetime.utcnow()

# 6) Write to Delta table
spark.createDataFrame(pdf).write.mode("overwrite").saveAsTable(out_table)
display(spark.read.table(out_table).limit(10))
print("✅ Embedded data written to", out_table)
