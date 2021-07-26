from textwrap import dedent

from airflow import DAG
from airflow.utils.dates import days_ago

from open_bus_pipelines.dags_generator import dags_generator
from open_bus_pipelines.operators.api_bash_operator import ApiBashOperator
from open_bus_pipelines.config import OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS


for dag_id, dag in dags_generator('https://raw.githubusercontent.com/hasadna/open-bus-siri-etl/main/'):
    globals()[dag_id] = dag


# following dags require some additional logic so they are declared here rather then in the airflow.yaml

dag_kwargs = dict(
    default_args={
        'owner': 'airflow',
    },
    schedule_interval=None,
    start_date=days_ago(2),
)
if OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS:
    with DAG('siri-etl-download-latest-snapshots', **dag_kwargs) as download_latest_snapshots_dag:
        ApiBashOperator(
            {
                'type': 'api',
                'module': 'open_bus_siri_etl.local_development_helpers',
                'function': 'download_latest_snapshots'
            },
            task_id='download_latest_snapshots'
        )
else:
    with DAG('siri-etl-list-latest-snapshots', **dag_kwargs) as list_latest_snapshots_dag:
        ApiBashOperator(
            {
                'type': 'cli',
                'module': 'open_bus_siri_requester.cli',
                'function': 'storage_list',
                'kwargs': {
                    'snapshot_id_prefix': {},
                    'limit': {'default': 200}
                }
            },
            task_id='list_latest_snapshots'
        )

