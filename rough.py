from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, FloatType
import requests
import json

# Configuration
CATALOG = "dsenprod"
SCHEMA = "lit_prepare"
SOURCE_TABLE = "your_source_table_name"  # Replace with your actual table name
TARGET_TABLE = "your_target_table_name"  # Replace with your desired target table name
EMBEDDING_MODEL = "sister_v2_small"

# Full table names
source_table_full = f"{CATALOG}.{SCHEMA}.{SOURCE_TABLE}"
target_table_full = f"{CATALOG}.{SCHEMA}.{TARGET_TABLE}"

# Read the source table
df = spark.table(source_table_full)

print(f"Loaded {df.count()} rows from {source_table_full}")

# Get Databricks token and host for API calls
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
host = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

# Function to get embeddings from Databricks serving endpoint
def get_embedding(text):
    """
    Get embedding for a single text string.
    Returns a list of floats (the embedding vector).
    """
    if text is None or str(text).strip() == "":
        return None
    
    url = f"{host}/serving-endpoints/{EMBEDDING_MODEL}/invocations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Correct payload format based on sister_v2_small model requirements
    payload = {
        "inputs": [str(text)]  # Must be "inputs" (plural) with a list
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Extract embedding from response - sister_v2_small returns "predictions"
        if isinstance(result, dict) and "predictions" in result:
            predictions = result["predictions"]
            if isinstance(predictions, list) and len(predictions) > 0:
                # Return the first prediction (embedding vector)
                return predictions[0]
        
        print(f"Unexpected response format: {result}")
        return None
        
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        return None

# Register UDF with proper return type
get_embedding_udf = F.udf(get_embedding, ArrayType(FloatType()))

# Add embedded columns
# Cast text columns to string explicitly to avoid any type issues
df_with_embeddings = df.withColumn(
    "Finding_Embedding",
    get_embedding_udf(F.col("Finding").cast("string"))
).withColumn(
    "Action_Embedding",
    get_embedding_udf(F.col("Action").cast("string"))
)

# Show sample to verify
print("\nSample of embedded data:")
df_with_embeddings.select("Id", "Finding", "Action").show(5, truncate=50)

# Check if embeddings were generated
embedding_check = df_with_embeddings.select(
    F.sum(F.when(F.col("Finding_Embedding").isNotNull(), 1).otherwise(0)).alias("finding_embeddings_count"),
    F.sum(F.when(F.col("Action_Embedding").isNotNull(), 1).otherwise(0)).alias("action_embeddings_count")
).collect()[0]

print(f"\nEmbeddings generated:")
print(f"Finding embeddings: {embedding_check['finding_embeddings_count']}")
print(f"Action embeddings: {embedding_check['action_embeddings_count']}")

# Write to target table
print(f"\nWriting to {target_table_full}...")
df_with_embeddings.write.mode("overwrite").saveAsTable(target_table_full)

print(f"\nSuccess! Table {target_table_full} created with {df_with_embeddings.count()} rows.")

# Verify the final table
final_df = spark.table(target_table_full)
print("\nFinal table schema:")
final_df.printSchema()
print(f"\nFinal table row count: {final_df.count()}")
