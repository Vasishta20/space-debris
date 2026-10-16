# Project-local Hive rollups

`queries.hql` defines the historical conjunction schema and shell/operator rollup. It must be run only against an independently sourced event/CDM export. SATCAT is not a conjunction-event table and must not be loaded as one.

Expected input fields are documented in the table definition. Required fields are `event_id`, `tca_utc`, object IDs, miss distance in km, relative velocity in km/s, coordinate frame, source URI, retrieval timestamp, and `altitude_shell`; operator fields may be null.

The current WSL2 distribution has no `hive` command, so no Hive execution is claimed. After an isolated Hive runtime is intentionally provisioned, a bounded command is:

```bash
hive --hiveconf input_path=/absolute/path/events.parquet \
     --hiveconf altitude_shell=15 \
     -f /mnt/c/space-debris-collision-risk-output/project/hive/queries.hql
```

This command must be run per validated partition or replaced by an approved external-table load. Preserve the original source file, retrieval metadata, row counts, and Hive logs.
