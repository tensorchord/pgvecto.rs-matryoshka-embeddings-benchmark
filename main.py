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
