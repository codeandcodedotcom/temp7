# Define the catalog and schema
catalog = "dsenprd"
schema = "lit_prepare"

delta_table_1 = f"{catalog}.{schema}.prepare_historical_data"
embedding_table_1 = f"{catalog}.{schema}.embedding_prepare_historical_data"

from databricks_langchain import DatabricksEmbeddings
from pyspark.sql.types import StructType, ArrayType, FloatType
import pandas as pd

# Initialize the embedding model
embeddings = DatabricksEmbeddings(endpoint="sister_v2_small")

# Load source table and convert to Pandas
df = spark.table(delta_table_1)
pdf = df.toPandas()

print(f"Processing {len(pdf)} rows...")

# Function to safely embed text
def safe_embed(text):
    if pd.isna(text) or text == "" or text is None:
        return None
    try:
        return embeddings.embed_query(str(text))
    except Exception as e:
        print(f"Error embedding text: {e}")
        return None

# Generate embeddings for both columns
pdf['finding_embedding'] = pdf['Finding'].apply(safe_embed)
pdf['action_embedding'] = pdf['Action'].apply(safe_embed)

print("Embeddings generated. Converting back to Spark DataFrame...")

# Convert back to Spark DataFrame
df_with_embeddings = spark.createDataFrame(pdf)

# Write the result to a new table
df_with_embeddings.write.mode("overwrite").saveAsTable(embedding_table_1)

print("Table saved successfully!")

# Show the resulting DataFrame
display(df_with_embeddings)
