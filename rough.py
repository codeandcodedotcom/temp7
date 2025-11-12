# Define the catalog and schema
catalog = "dsenprd"
schema = "lit_prepare"

delta_table_1 = f"{catalog}.{schema}.prepare_historical_data"
embedding_table_1 = f"{catalog}.{schema}.embedding_prepare_historical_data"

from databricks_langchain import DatabricksEmbeddings
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, FloatType, IntegerType, TimestampType
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
        result = embeddings.embed_query(str(text))
        # Convert to list of floats to ensure proper format
        return [float(x) for x in result]
    except Exception as e:
        print(f"Error embedding text '{str(text)[:50]}...': {e}")
        return None

# Generate embeddings for both columns
pdf['finding_embedding'] = pdf['Finding'].apply(safe_embed)
pdf['action_embedding'] = pdf['Action'].apply(safe_embed)

print("Embeddings generated. Converting back to Spark DataFrame...")

# Get the original schema and add embedding columns
original_schema = df.schema
new_schema = StructType(
    original_schema.fields + [
        StructField("finding_embedding", ArrayType(FloatType()), True),
        StructField("action_embedding", ArrayType(FloatType()), True)
    ]
)

# Convert back to Spark DataFrame with explicit schema
df_with_embeddings = spark.createDataFrame(pdf, schema=new_schema)

# Write the result to a new table
df_with_embeddings.write.mode("overwrite").saveAsTable(embedding_table_1)

print("Table saved successfully!")

# Show the resulting DataFrame
display(df_with_embeddings)
