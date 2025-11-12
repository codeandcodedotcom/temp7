# Define the catalog and schema
catalog = "dsenprd"
schema = "lit_prepare"

delta_table_1 = f"{catalog}.{schema}.prepare_historical_data"
embedding_table_1 = f"{catalog}.{schema}.embedding_prepare_historical_data"

from databricks_langchain import DatabricksEmbeddings
from pyspark.sql.functions import pandas_udf, col
from pyspark.sql.types import ArrayType, FloatType
import pandas as pd

# Initialize the embedding model
embeddings = DatabricksEmbeddings(endpoint="sister_v2_small")

# Pandas UDF to embed a batch of texts
@pandas_udf(ArrayType(FloatType()))
def embed_batch(texts: pd.Series) -> pd.Series:
    return texts.apply(lambda t: embeddings.embed_query(t) if t is not None else None)

# Load source table
df = spark.table(delta_table_1)

# Generate embeddings for both columns - use col() to reference columns
df_with_embeddings = (
    df
    .withColumn("finding_embedding", embed_batch(col("Finding")))
    .withColumn("action_embedding", embed_batch(col("Action")))
)

# Write the result to a new table (includes original columns + embeddings)
df_with_embeddings.write.mode("overwrite").saveAsTable(embedding_table_1)

# Show the resulting DataFrame
display(df_with_embeddings)
