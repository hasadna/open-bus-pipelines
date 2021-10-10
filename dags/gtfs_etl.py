from open_bus_pipelines.dags_generator import dags_generator


# GTFS_ETL_URL_OR_PATH = '../open-bus-gtfs-etl/'
GTFS_ETL_URL_OR_PATH = 'https://raw.githubusercontent.com/hasadna/open-bus-gtfs-etl/main/'


for dag_id, dag in dags_generator(GTFS_ETL_URL_OR_PATH):
    globals()[dag_id] = dag
