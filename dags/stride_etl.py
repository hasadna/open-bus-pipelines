from open_bus_pipelines.dags_generator import dags_generator


for dag_id, dag in dags_generator('https://raw.githubusercontent.com/hasadna/open-bus-stride-etl/main/'):
    globals()[dag_id] = dag
