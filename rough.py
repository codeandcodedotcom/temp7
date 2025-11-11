# ---------------- CONFIG ----------------
catalog = "dsenprd"
schema = "lit_prepare"

src_table = f"{catalog}.{schema}.prepare_historical_data"
out_table = f"{catalog}.{schema}.embedding_prepare_historical_data"

BATCH_SIZE = 200   # safe for 419 rows
# ----------------------------------------

from databricks_langchain import DatabricksEmbeddings
import pandas as pd
import numpy as np
from datetime import datetime

# Initialize embedding model
embedder = DatabricksEmbeddings(endpoint="sister_v2_small")

# 1️⃣ Load data (test small subset first)
pdf = (
    spark.read.table(src_table)
    .select("id", "Finding", "Action")
    # .limit(10)   # 👈 uncomment for a quick test run
    .toPandas()
)

# 2️⃣ Helper to embed in batches
def batch_embed(texts, batch_size=BATCH_SIZE):
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # returns list of numpy arrays
        embs = [embedder.embed_query(t) for t in batch]
        all_embs.extend(embs)
    return all_embs

# 3️⃣ Create clean text lists
findings = pdf["Finding"].fillna("").astype(str).tolist()
actions  = pdf["Action"].fillna("").astype(str).tolist()

# 4️⃣ Embed both columns
finding_embs = batch_embed(findings)
action_embs  = batch_embed(actions)

# 5️⃣ Forcefully convert every embedding to a plain list of floats
def to_plain_list(v):
    if v is None:
        return []
    if isinstance(v, np.ndarray):
        return [float(x) for x in v.tolist()]
    if isinstance(v, (list, tuple)):
        return [float(x) for x in v]
    return [float(v)]

pdf["finding_embedding"] = [to_plain_list(v) for v in finding_embs]
pdf["action_embedding"]  = [to_plain_list(v) for v in action_embs]
pdf["ingestion_ts"] = datetime.utcnow()

# ✅ This step guarantees Spark sees only pure Python objects
pdf = pdf.applymap(
    lambda v: [float(x) for x in v] if isinstance(v, np.ndarray) else v
)

# 6️⃣ Create Spark DataFrame safely and save as Delta
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType, TimestampType
from pyspark.sql import Row

schema = StructType([
    StructField("id", StringType(), True),
    StructField("Finding", StringType(), True),
    StructField("Action", StringType(), True),
    StructField("finding_embedding", ArrayType(DoubleType()), True),
    StructField("action_embedding", ArrayType(DoubleType()), True),
    StructField("ingestion_ts", TimestampType(), True),
])

rows = [
    Row(
        id=str(r["id"]),
        Finding=r["Finding"],
        Action=r["Action"],
        finding_embedding=r["finding_embedding"],
        action_embedding=r["action_embedding"],
        ingestion_ts=r["ingestion_ts"]
    )
    for _, r in pdf.iterrows()
]

sdf = spark.createDataFrame(rows, schema=schema)
sdf.write.mode("overwrite").saveAsTable(out_table)

print(f"✅ Embedded {len(pdf)} rows and saved to {out_table}")
display(spark.read.table(out_table).limit(10))
