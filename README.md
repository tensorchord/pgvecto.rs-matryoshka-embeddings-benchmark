# Matryoshka embeddings benchmark in pgvecto.rs

## What is Matryoshka embeddings

https://aniketrege.github.io/blog/2024/mrl/#what-is-mrl-really-this-time

## Benchmark setup

### Low dimensional embedding index

Create the table with the following SQL command:

```sql
CREATE TABLE openai3072 (
  id bigserial PRIMARY KEY,
  text_embedding_3_large_3072_embedding vector(3072)
);
```

Create index with the following SQL command:

```sql
CREATE INDEX openai_vector_index on openai3072 using vectors((text_embedding_3_large_3072_embedding[0:1024]::vector(1024)) vector_l2_ops);
```

Please note that we only use the first 1024 dimensions of the 3072-dimensional embeddings for the index.

Then run the following command to create index for the first 256 dimensions:

```sql
CREATE INDEX openai_vector_index_256 ON public.openai3072 USING vectors (((text_embedding_3_large_3072_embedding[0:256])::vector(256)) vector_l2_ops);
```

#### Adaptive retrieval with 256-dimensional index

```sql
CREATE OR REPLACE FUNCTION match_documents_adaptive(
  query_embedding vector(3072),
  match_count int
)
RETURNS SETOF openai3072
LANGUAGE SQL
AS $$
WITH shortlist AS (
  SELECT *
  FROM openai3072
  ORDER BY (text_embedding_3_large_3072_embedding[0:256])::vector(256) <=> (query_embedding[0:256])::vector(256)
  LIMIT match_count * 8
)
SELECT *
FROM shortlist
ORDER BY text_embedding_3_large_3072_embedding <=> query_embedding
LIMIT match_count;
$$;
```

### Data ingestion

```python
from pgvecto_rs.sdk import PGVectoRs, Record
from pgvecto_rs.psycopg import register_vector
import psycopg

conn = psycopg.connect(conninfo='postgresql://postgres:mysecretpassword@localhost:5433/postgres', autocommit=True)

import json
import os

import numpy as np
import random
from datasets import load_dataset
from datasets.exceptions import DatasetNotFoundError
from tqdm import tqdm

MODEL_NAME, DIMENSIONS = "text-embedding-3-large", 3072
DATASET_NAME = f"Qdrant/dbpedia-entities-openai3-{MODEL_NAME}-{DIMENSIONS}-1M"
collection_name = f"dbpedia-{MODEL_NAME}-{DIMENSIONS}"
embedding_column_name = f"{MODEL_NAME}-{DIMENSIONS}-embedding"

dataset = load_dataset(
        DATASET_NAME,
        streaming=False,
        split="train",
    )

bs = 1000
for i, record in tqdm(enumerate(dataset)):
    if i % bs == 0:
        points = []
    points.append({
        "embedding": record[embedding_column_name]
    })
    if i % bs == bs - 1:
        batch_points = f", ".join([f"('{p['embedding']}')" for p in points])
        conn.execute(f"INSERT INTO openai3072 (text_embedding_3_large_3072_embedding) VALUES %s" % (batch_points))
    print(f"Inserted {i} records")
```
