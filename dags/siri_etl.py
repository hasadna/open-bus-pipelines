from airflow import DAG
from airflow.utils.dates import days_ago

from open_bus_pipelines.operators.api_bash_operator import ApiBashOperator
from open_bus_pipelines.config import OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS


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
            config={
                'type': 'api',
                'module': 'open_bus_siri_etl.local_development_helpers',
                'function': 'download_latest_snapshots'
            },
            task_id='download_latest_snapshots'
        )
else:
    with DAG('siri-etl-list-latest-snapshots', **dag_kwargs) as list_latest_snapshots_dag:
        ApiBashOperator(
            config={
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

