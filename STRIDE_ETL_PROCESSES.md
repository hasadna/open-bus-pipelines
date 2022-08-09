# Open Bus Stride ETL Processes

## siri-requester-daemon

A daemon which runs continuously and approximately every 60 seconds downloads the latest SIRI snapshot from MOT.

## siri-etl-process-snapshot-new-snapshots-daemon

A daemon which runs continuously and approximately every 60 seconds looks for new SIRI snapshots loaded by [siri-requester-daemon](#siri-requester-daemon).
It then loads all the data from the downloaded SIRI snapshots to the DB tables [siri_ride](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride), [siri_ride_stop](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride_stop), [siri_route](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_route), 
[siri_stop](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_stop), [siri_vehicle_location](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_vehicle_location). It uses the [siri_snapshot](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_snapshot) table to track progress of each snapshot loading.

## gtfs-etl-download-upload

Runs hourly, downloads the daily GTFS data from MOT if not downloaded yet and uploads to S3
Downloaded data is available in the following format:
`https://openbus-stride-public.s3.eu-west-1.amazonaws.com/gtfs_archive/year/month/dat/filename`,
for example: https://openbus-stride-public.s3.eu-west-1.amazonaws.com/gtfs_archive/2022/06/03/ClusterToLine.zip
possible values for filename: `ClusterToLine.zip`, `Tariff.zip`, `TripIdToDate.zip`, `israel-public-transportation.zip`.

## gtfs-etl-process

Runs hourly, iterates over all dates for which we have data for and makes sure all of them were processed

## siri-etl-update-pending-snapshots

Check all raw snapshot files in both local and remote (S3) storage,
snapshots which don't exist in DB siri_snapshots table are added with status pending.

## stride-etl-siri-add-ride-durations

Runs hourly, finds the first and last vehicle location of each ride and 
updates the following fields in DB: [siri_ride.duration_minutes](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_rideduration_minutes),
[siri_ride.first_vehicle_location_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ridefirst_vehicle_location_id), [siri_ride.last_vehicle_location_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ridelast_vehicle_location_id).

## stride-etl-siri-update-ride-stops-gtfs

Runs hourly, tries to match SIRI stops with GTFS stops and updates the following field in DB: [siri_ride_stop.gtfs_stop_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride_stopgtfs_stop_id).

## stride-etl-siri-update-ride-stops-vehicle-locations

Runs hourly, looks for siri ride stops which have a matching gtfs stop 
and uses the gtfs stop lon/lat to update the following fields in DB: 
[siri_vehicle_location.distance_from_siri_ride_stop_meters](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_vehicle_locationdistance_from_siri_ride_stop_meters), 
[siri_ride_stop.nearest_siri_vehicle_location_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride_stopnearest_siri_vehicle_location_id).

## stride-etl-siri-update-rides-gtfs

Runs hourly, looks for matching between siri rides and gtfs rides and updates
the following DB fields: [siri_ride.route_gtfs_ride_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_rideroute_gtfs_ride_id), 
[siri_ride.journey_gtfs_ride_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ridejourney_gtfs_ride_id), [siri_ride.gtfs_ride_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ridegtfs_ride_id).

## stride-etl-siri-storage-backup-cleanup

Runs hourly, uploads raw SIRI data to S3 in the following format:
`https://openbus-stride-public.s3.eu-west-1.amazonaws.com/stride-siri-requester/year/month/day/hour/minute.br`
for example: 
https://openbus-stride-public.s3.eu-west-1.amazonaws.com/stride-siri-requester/2022/06/03/08/54.br
The file is compressed using brotli.

## stride-etl-gtfs-update-ride-aggregations

Idempotent task, runs hourly and verifies that the data is up to date.

It updates the following fields in DB: [gtfs_ride.first_gtfs_ride_stop_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_ridefirst_gtfs_ride_stop_id), [gtfs_ride.last_gtfs_ride_stop_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_ridelast_gtfs_ride_stop_id), 
[gtfs_ride.start_time](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_ridestart_time), [gtfs_ride.end_time](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_rideend_time).

## stride-etl-urbanaccess-update-areas-fake-gtfs

Runs daily, updates fake gtfs data for urbanaccess areas.
Makes sure there is daily fake gtfs data for each area for the last 30 days.
Data is avilable for download via the artifacts API method.

