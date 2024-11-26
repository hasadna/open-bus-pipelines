# Open Bus Stride ETL Processes

This document is generated automatically from etl process definitions.
Click on the process name to see the related source code.

## [siri-requester-daemon](https://www.github.com/hasadna/open-bus-siri-requester/tree/main/open_bus_siri_requester)

A daemon which runs continuously and approximately every 60 seconds downloads the latest SIRI snapshot from MOT.

## [siri-etl-process-snapshot-new-snapshots-daemon](https://www.github.com/hasadna/open-bus-siri-etl/tree/main/open_bus_siri_etl)

A daemon which runs continuously and approximately every 60 seconds looks for new SIRI snapshots loaded by [siri-requester-daemon](#siri-requester-daemon).
It then loads all the data from the downloaded SIRI snapshots to the DB tables [siri_ride](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride), [siri_ride_stop](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride_stop), [siri_route](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_route), 
[siri_stop](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_stop), [siri_vehicle_location](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_vehicle_location). It uses the [siri_snapshot](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_snapshot) table to track progress of each snapshot loading.

Most of the processing is done in [process_snapshot.py](https://github.com/hasadna/open-bus-siri-etl/blob/main/open_bus_siri_etl/process_snapshot.py)
process_snapshot function. This functions gets the SIRI snapshot data, parses it and loads to DB tables.
The full spec of the SIRI snapshot data is available [here](https://www.gov.il/he/departments/general/real_time_information_siri)
as a PDF file under "SIRI-SM / ICD SM".

## [gtfs-etl-download-upload](https://www.github.com/hasadna/open-bus-gtfs-etl/tree/main/open_bus_gtfs_etl)

Runs hourly, downloads the daily GTFS data from MOT if not downloaded yet and uploads to S3
Downloaded data is available in the following format:
`https://openbus-stride-public.s3.eu-west-1.amazonaws.com/gtfs_archive/year/month/dat/filename`,
for example: https://openbus-stride-public.s3.eu-west-1.amazonaws.com/gtfs_archive/2022/06/03/ClusterToLine.zip
possible values for filename: `ClusterToLine.zip`, `Tariff.zip`, `TripIdToDate.zip`, `israel-public-transportation.zip`.

## [gtfs-etl-process](https://www.github.com/hasadna/open-bus-gtfs-etl/tree/main/open_bus_gtfs_etl)

Runs hourly, iterates over all dates for which we have data for and makes sure all of them were processed

## [siri-etl-validate-snapshots](https://www.github.com/hasadna/open-bus-siri-etl/tree/main/open_bus_siri_etl)

Runs manually, compare snapshots in range between the data in DB and the raw snapshot data.
Generates a csv file where each row contains a mismatch between the DB and raw snapshot data.
{
    "snapshot_id_from": "2021/07/05/12/50",
    "snapshot_id_to": "2021/07/05/12/55"
}

## [siri-etl-update-pending-snapshots](https://www.github.com/hasadna/open-bus-siri-etl/tree/main/open_bus_siri_etl)

Runs daily, checks all raw snapshot files in both local and remote (S3) storage,
snapshots which don't exist in DB siri_snapshots table are added with status pending.

## [siri-etl-process-old-missing-snapshots](https://www.github.com/hasadna/open-bus-siri-etl/tree/main/open_bus_siri_etl)

Runs daily, iterates over siri_snapshots which have status pending and older then 24 hours,
runs processing for those snapshots to update their data in DB.

## [stride-etl-siri-update-ride-stops-gtfs](https://www.github.com/hasadna/open-bus-stride-etl/tree/main/open_bus_stride_etl/siri)

Runs hourly, tries to match SIRI stops with GTFS stops and updates the following field in DB: [siri_ride_stop.gtfs_stop_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride_stopgtfs_stop_id).

## [stride-etl-siri-update-ride-stops-vehicle-locations](https://www.github.com/hasadna/open-bus-stride-etl/tree/main/open_bus_stride_etl/siri)

Runs hourly, looks for siri ride stops which have a matching gtfs stop 
and uses the gtfs stop lon/lat to update the following fields in DB: 
[siri_vehicle_location.distance_from_siri_ride_stop_meters](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_vehicle_locationdistance_from_siri_ride_stop_meters), 
[siri_ride_stop.nearest_siri_vehicle_location_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ride_stopnearest_siri_vehicle_location_id).

## [stride-etl-siri-update-rides-gtfs](https://www.github.com/hasadna/open-bus-stride-etl/tree/main/open_bus_stride_etl/siri)

Runs hourly, looks for matching between siri rides and gtfs rides and updates
the following DB fields: [siri_ride.route_gtfs_ride_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_rideroute_gtfs_ride_id), 
[siri_ride.journey_gtfs_ride_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ridejourney_gtfs_ride_id), [siri_ride.gtfs_ride_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#siri_ridegtfs_ride_id).

## [stride-etl-siri-storage-backup-cleanup](https://www.github.com/hasadna/open-bus-stride-etl/tree/main/open_bus_stride_etl/siri)

Runs hourly, uploads raw SIRI data to S3 in the following format:
`https://openbus-stride-public.s3.eu-west-1.amazonaws.com/stride-siri-requester/year/month/day/hour/minute.br`
for example: 
https://openbus-stride-public.s3.eu-west-1.amazonaws.com/stride-siri-requester/2022/06/03/08/54.br
The file is compressed using brotli.

## [stride-etl-gtfs-update-ride-aggregations](https://www.github.com/hasadna/open-bus-stride-etl/tree/main/open_bus_stride_etl/gtfs)

Idempotent task, runs hourly and verifies that the data is up to date.

It updates the following fields in DB: [gtfs_ride.first_gtfs_ride_stop_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_ridefirst_gtfs_ride_stop_id), [gtfs_ride.last_gtfs_ride_stop_id](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_ridelast_gtfs_ride_stop_id), 
[gtfs_ride.start_time](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_ridestart_time), [gtfs_ride.end_time](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#gtfs_rideend_time).

## [stride-etl-urbanaccess-update-areas-fake-gtfs](https://www.github.com/hasadna/open-bus-stride-etl/tree/main/open_bus_stride_etl/urbanaccess)

Runs daily, updates fake gtfs data for urbanaccess areas.
Makes sure there is daily fake gtfs data for each area for the last 30 days.
Data is avilable for download via the artifacts API method.

## [stride-etl-packagers-siri-update-package](https://www.github.com/hasadna/open-bus-stride-etl/tree/main/open_bus_stride_etl/packagers)

Collect SIRI data and save in storage

