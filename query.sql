\set random_id random(1, 1000000)

-- select id from openai3072 order by text_embedding_3_large_3072_bvector <-> (select text_embedding_3_large_3072_bvector from openai3072 where id = :random_id) limit 5;

select id from match_documents_adaptive_bvector_m2((select text_embedding_3_large_3072_embedding from openai3072 where id = :random_id), (select text_embedding_3_large_3072_bvector from openai3072 where id = :random_id), 100);
