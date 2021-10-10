import requests
from ruamel import yaml
from airflow import DAG
from airflow.utils.dates import days_ago

from open_bus_pipelines.operators.api_bash_operator import ApiBashOperator


def yaml_safe_load(url_or_path):
    if url_or_path.startswith('http'):
        return yaml.safe_load(requests.get(url_or_path).text)
    else:
        with open(url_or_path) as f:
            return yaml.safe_load(f)


def dags_generator(base_url):
    dag_kwargs = dict(
        default_args={
            'owner': 'airflow',
        },
        start_date=days_ago(2),
        catchup=False
    )
    for dags_filename in yaml_safe_load(base_url + 'airflow.yaml').get('dag_files', []):
        for dag_config in yaml_safe_load(base_url + dags_filename):
            with DAG(
                dag_config['name'],
                description=dag_config.get('description', ''),
                schedule_interval=dag_config.get('schedule_interval', None),
                **dag_kwargs,
            ) as dag:
                tasks = {}
                for task_config in dag_config['tasks']:
                    tasks[task_config['id']] = ApiBashOperator(
                        task_config['config'],
                        task_id=task_config['id']
                    )
                    if task_config.get('depends_on'):
                        for depends_on_task_id in task_config['depends_on']:
                            tasks[task_config['id']].set_upstream(tasks[depends_on_task_id])
                yield dag_config['name'].replace('-', '_'), dag
