from open_bus_pipelines.dags_generator import dags_generator, yaml_safe_load


ETL_INDEX_URL_OR_PATH = 'https://raw.githubusercontent.com/hasadna/open-bus-pipelines/main/etl_index.yaml'
for etl in yaml_safe_load(ETL_INDEX_URL_OR_PATH):
    url_or_path = etl.get('url', etl.get('path'))
    for dag_id, dag in dags_generator(url_or_path):
        globals()[dag_id] = dag
