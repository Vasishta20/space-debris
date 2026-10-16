CREATE KEYSPACE IF NOT EXISTS space_debris
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS space_debris.object_state_by_bucket (
  object_id text,
  time_bucket text,
  epoch_utc timestamp,
  position_x_km double,
  position_y_km double,
  position_z_km double,
  velocity_x_km_s double,
  velocity_y_km_s double,
  velocity_z_km_s double,
  coordinate_frame text,
  source_uri text,
  PRIMARY KEY ((object_id, time_bucket), epoch_utc)
) WITH CLUSTERING ORDER BY (epoch_utc DESC);
