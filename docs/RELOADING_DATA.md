# Reloading Data

The following procedure can be used to reload data to the DB.
This can be useful for local development as well as cases where data in DB is invalid and 
needs to be reloaded.

This procedure describes Airflow dags which need to run, you can deduce the corresponding
project / CLI command from the dag id and use it to run it locally.
For example, dag id `siri-etl-parallel-process-old-missing-snapshots` corresponds to project
`open-bus-siri-etl` CLI subcommand `parallel-process-old-missing-snapshots`

Check the Airflow dag description or CLI command help for available parameters, you will
usually need to set from/to dates. It's recommended to start with a small reload of all tasks
and if successful progressively load more history. 

All tasks have to run in the following order due to data dependencies.

### `stride-etl-db-copy-backup-to-s3`

It's recommended to run this before reloading to have the option of rollback in case of problems.

### `siri-etl-parallel-process-old-missing-snapshots`

This task takes a significant amount of time, as it loads each snapshot to the DB.
It supports parallelization, but that does increase the load on the DB, so use with caution.
It's recommended to specify 2 parallel processes, and keep monitoring the DB and other tasks
for failures due to DB load. The task only loads missing snapshots, so if snapshots failed
you can just re-run it to retry any errors.

### `gtfs-etl-load-missing-data`

### `stride-etl-gtfs-update-ride-aggregations-date-range`

### `stride-etl-siri-add-ride-durations`

This dag runs every hour and repopulates all ride durations. The hourly run will update
all new rides automatically, you don't need to run this manually. If you want to recalculate
ride durations, you can update `siri_ride.updated_duration_minutes` field in DB to null
and this task will recalculate the ride duration for that ride.

### `stride-etl-siri-update-ride-stops-gtfs`

### `stride-etl-siri-update-ride-stops-vehicle-locations`

### `stride-etl-siri-update-rides-gtfs`
