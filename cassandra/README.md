# Project-local Cassandra readiness

The proposed table uses `((object_id, time_bucket), epoch_utc)` so an object’s bounded time bucket is the partition key and epoch provides ordered state lookup. The CQL schema is in `schema.cql`; the optional Python adapter is `app/cassandra_store.py`.

The current WSL2 distribution has no `cassandra` or `cqlsh` command. No Cassandra process, dependency installation, or API integration was performed. PostgreSQL/SQLite remain the active application backends. Once an isolated Cassandra runtime is approved, execute `schema.cql`, load a small user-approved state subset, and record actual upsert/read counts and logs.
