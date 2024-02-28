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

ds = dataset.train_test_split(test_size=0.001, shuffle=True, seed=37)["test"]
ds = ds.to_pandas().to_dict(orient="records")

from pgvecto_rs.sdk import PGVectoRs, Record
from pgvecto_rs.psycopg import register_vector
import psycopg

conn = psycopg.connect(conninfo='postgresql://postgres:mysecretpassword@localhost:5433/postgres', autocommit=True)

# c = conn.execute("select text_embedding_3_large_3072_embedding from openai3072 where id =1")
# print("c", c.fetchall())

limit_range = [100, 50, 20, 10, 5]
with open("results.txt", "w") as f:
    for element in tqdm(ds):
        for limit in limit_range:
            c = conn.execute(f"SELECT * FROM match_documents_adaptive('%s', %s)" % ("[" + ", ".join([str(e) for e in element[embedding_column_name]]) + "]", limit))
            records = c.fetchall()
            hnsw256 = [item[0] for item in records]
        
            c = conn.execute(f"SELECT * FROM match_documents_adaptive_1024('%s', %s)" % ("[" + ", ".join([str(e) for e in element[embedding_column_name]]) + "]", limit))
            records = c.fetchall()
            hnsw1024 = [item[0] for item in records]

            c = conn.execute(f"SELECT * FROM openai3072 ORDER BY text_embedding_3_large_3072_embedding <-> '%s' LIMIT {limit}" % ("[" + ", ".join([str(e) for e in element[embedding_column_name]]) + "]"))
            records = c.fetchall()
            exact_ids = [item[0] for item in records]

            accuracy1024 = len(set(exact_ids) & set(hnsw1024)) / len(exact_ids)
            accuracy256 = len(set(exact_ids) & set(hnsw256)) / len(exact_ids)
            print(f"limit: {limit}, accuracy1024: {accuracy1024}, accuracy256: {accuracy256}")
            f.write(f"{element['_id']},{limit},{accuracy1024},{accuracy256}\n")
