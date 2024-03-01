export PGHOST="localhost"
export PGUSER="postgres"
export PGPASSWORD="mysecretpassword"
export PGDATABASE="postgres"
export PGPORT=5433
export VECTOR_DIM=3072
TEST_TIME=300
VECTOR_OPS="vector_l2_ops"
for clients in 4 8 16; do
    pgbench -n -T "${TEST_TIME}" \
      --file=query.sql \
      -c "${clients}" -j "${clients}"
done
