-- Project-local Hive definitions for user-supplied historical conjunction data.
-- No current project dataset is loaded by this file. The input must be an
-- independently sourced CDM/event export with the documented columns.

CREATE DATABASE IF NOT EXISTS space_debris;
USE space_debris;

CREATE TABLE IF NOT EXISTS historical_conjunctions (
  event_id STRING,
  tca_utc TIMESTAMP,
  primary_object_id STRING,
  chaser_object_id STRING,
  primary_operator STRING,
  chaser_operator STRING,
  miss_distance_km DOUBLE,
  relative_velocity_km_s DOUBLE,
  coordinate_frame STRING,
  source_uri STRING,
  source_retrieved_utc TIMESTAMP
)
PARTITIONED BY (altitude_shell INT)
STORED AS PARQUET;

-- Example load command, intentionally not executed until a user-provided
-- validated file exists:
-- LOAD DATA LOCAL INPATH '${hivevar.input_path}' INTO TABLE historical_conjunctions
-- PARTITION (altitude_shell=${hivevar.altitude_shell});

CREATE TABLE IF NOT EXISTS conjunction_rollup_by_shell_operator (
  altitude_shell INT,
  operator STRING,
  event_count BIGINT,
  min_miss_distance_km DOUBLE,
  avg_miss_distance_km DOUBLE,
  avg_relative_velocity_km_s DOUBLE
)
STORED AS PARQUET;

-- Both participants contribute to an operator rollup. Null operators are
-- retained as '(unknown)' so null handling is explicit and counts remain
-- auditable. Empty input produces zero output rows.
INSERT OVERWRITE TABLE conjunction_rollup_by_shell_operator
SELECT altitude_shell, operator, COUNT(*) AS event_count,
       MIN(miss_distance_km), AVG(miss_distance_km),
       AVG(relative_velocity_km_s)
FROM (
  SELECT altitude_shell,
         COALESCE(primary_operator, '(unknown)') AS operator,
         event_id, miss_distance_km, relative_velocity_km_s
  FROM historical_conjunctions
  UNION ALL
  SELECT altitude_shell,
         COALESCE(chaser_operator, '(unknown)') AS operator,
         event_id, miss_distance_km, relative_velocity_km_s
  FROM historical_conjunctions
) participants
GROUP BY altitude_shell, operator;
