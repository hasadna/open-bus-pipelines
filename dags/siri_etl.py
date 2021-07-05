from textwrap import dedent

from airflow import DAG
from airflow.utils.dates import days_ago

from open_bus_pipelines.config import OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS
from open_bus_pipelines.operators.cli_bash_operator import CliBashOperator


dag_kwargs = dict(
    default_args={
        'owner': 'airflow',
    },
    schedule_interval=None,
    start_date=days_ago(2),
)


if OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS:
    with DAG('siri-etl-download-latest-snapshots', **dag_kwargs) as download_latest_snapshots_dag:
        CliBashOperator(
            'open-bus-siri-etl download-latest-snapshots',
            task_id='download_latest_snapshots'
        )
else:
    with DAG('siri-etl-list-latest-snapshots', **dag_kwargs) as list_latest_snapshots_dag:
        CliBashOperator(
            'open-bus-siri-requester storage-list',
            task_id='list_latest_snapshots'
        )


with DAG(
    'siri-etl-process-snapshot',
    description=dedent("""
        Process a single snapshot and load it to DB.
        {
            "snapshot_id": "2021/07/05/12/50",
            "force_reload": false
        }
    """),
    **dag_kwargs
) as process_snapshot_dag:
    CliBashOperator(
        dedent("""open-bus-siri-etl process-snapshot \\
            {{ "--force-reload" if dag_run.conf.get("force_reload") else "" }} \\
            {{ dag_run.conf["snapshot_id"] }}
        """),
        task_id='process_snapshot'
    )
