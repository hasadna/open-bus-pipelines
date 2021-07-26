import requests
from ruamel import yaml
from airflow import DAG
from airflow.utils.dates import days_ago

from open_bus_pipelines.operators.api_bash_operator import ApiBashOperator


def dags_generator(base_url):
    dag_kwargs = dict(
        default_args={
            'owner': 'airflow',
        },
        start_date=days_ago(2),
        catchup=False
    )
    for dags_filename in yaml.safe_load(requests.get(base_url + 'airflow.yaml').text).get('dag_files', []):
        for dag_config in yaml.safe_load(requests.get(base_url + dags_filename).text):
            with DAG(
                dag_config['name'],
                description=dag_config.get('description', ''),
                schedule_interval=dag_config.get('schedule_interval', None),
                **dag_kwargs,
            ) as dag:
                for task_config in dag_config['tasks']:
                    ApiBashOperator(
                        task_config['config'],
                        task_id=task_config['id']
                    )
                yield dag_config['name'].replace('-', '_'), dag
