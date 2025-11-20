from databricks.vector_search.client import VectorSearchClient
vc = VectorSearchClient()

# create endpoint if not created in UI
vc.create_endpoint(name="lessons-vs-endpoint", endpoint_type="STANDARD")



-----

from databricks.vector_search.client import VectorSearchClient

vc = VectorSearchClient()

index = vc.create_delta_sync_index(
    endpoint_name="lessons-vs-endpoint",                       # endpoint you created
    source_table_name="dsenprd.lit_prepare.embedding_prepare_historical_data",  
    index_name="lesson_learned_index",                        # your index name
    pipeline_type="ONE_TIME",                                 # ONE_TIME for static data (or TRIGGERED/CDC for updates)
    primary_key="id",                                         # unique id column in the table
    embedding_source_column="finding_embedding",              # the column with embeddings
    embedding_model_endpoint_name="sister_v2_small"           # name of embedding model used (for tracking)
)



---------

from databricks.vector_search.client import VectorSearchClient
from databricks_langchain import DatabricksEmbeddings   # or your embedder

# 1. embed user query
embedder = DatabricksEmbeddings(endpoint="sister_v2_small")
query_embedding = embedder.embed_query("My project description here")

# 2. load index object and query
vc = VectorSearchClient()
index = vc.get_index(endpoint_name="lessons-vs-endpoint", index_name="lesson_learned_index")

results = index.similarity_search(query_vector=query_embedding, columns=["Finding", "Action", "similarity"], top_k=5)

# results is a list of dicts — pick top result(s) to show Actions
for r in results:
    print(r["similarity"], r["Finding"], "=>", r["Action"])
