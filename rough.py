pdf = (
    spark.read.table(src_table)
    .select("id", "Finding", "Action")
    .limit(10)     # 👈 loads only 10 rows for testing
    .toPandas()
)
