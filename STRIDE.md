# Open Bus Stride

The goal of the Open Bus Stride project is to provide usable and accurate data about the Israeli public transportation system.

* Please report issues and feature requests [here](https://github.com/hasadna/open-bus/issues/new)
* To get updates about the system status and for general help join Hasadna's Slack #open-bus channel ([Hasadna Slack signup link](https://join.slack.com/t/hasadna/shared_invite/zt-167h764cg-J18ZcY1odoitq978IyMMig))

## Data Model

See the [Stride DB Data Model](https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md) for detailed description of all the data schema and objects.

See the available interfaces below for how to access this data.

For more details and background, see [MOT Developer Information](https://www.gov.il/BlobFolder/generalpage/gtfs_general_transit_feed_specifications/he/GTFS%20-%20Developer%20Information.pdf) for description of the source fields as published by the Israel Ministry of Transportation.

## ETL Processes

See the [Stride ETL Processes](https://github.com/hasadna/open-bus-pipelines/blob/main/STRIDE_ETL_PROCESSES.md) for detailed description of all ETL processes which load and process the data.

## Available Interfaces

**REST API**

This is the main interface which provides a REST API over the data model. 
See the [Stride API docs](https://open-bus-stride-api.hasadna.org.il/docs) for details.
See the [Stride API Usage guide](https://github.com/hasadna/open-bus-stride-api/blob/main/USAGE_GUIDE.md) for general usage of the REST API.

**Python Client**

A Python package which provides easy access to the Stride REST API. Also includes Jupyter Notebooks which demonstrate how to use the API.
See the [Python Client README](https://github.com/hasadna/open-bus-stride-client/blob/main/README.md) for details.

**SQL Database**

We don't provide public access to the database due to complexity and scale issues. It's recommended to use the API instead.
If you require some data which is not available via the API or require direct access to the DB, please [open an issue](https://github.com/hasadna/open-bus/issues/new).
