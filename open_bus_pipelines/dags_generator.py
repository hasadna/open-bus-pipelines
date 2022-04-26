import os
import time
import json
import hashlib
import datetime
import traceback

import requests
from ruamel import yaml
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from open_bus_pipelines.operators.api_bash_operator import ApiBashOperator


CACHE_PATH = '/var/airflow/open-bus-pipelines-dags-cache'


def get_from_url(url):
    cache_key = hashlib.sha256(url.encode()).hexdigest()
    cache_filename = os.path.join(CACHE_PATH, cache_key + '.json')
    os.makedirs(CACHE_PATH, exist_ok=True)
    res = None
    for i in range(10):
        if i != 0:
            print("Failed to get from url, will retry in 10 seconds...")
            time.sleep(10)
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            res = response.text
            break
        except:
            traceback.print_exc()
    if res is not None:
        with open(cache_filename, 'w') as f:
            json.dump({
                'url': url,
                'datetime': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z'),
                'text': res
            }, f)
        return res
    else:
        if os.path.exists(cache_filename):
            print("Failed to get from url, trying from local cache")
            with open(cache_filename) as f:
                data = json.load(f)
            dt = datetime.datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M:%S%z')
            if dt + datetime.timedelta(days=5) <= datetime.datetime.now(datetime.timezone.utc):
                raise Exception("Local cache is too old")
            else:
                return data['text']
        else:
            raise Exception("No local cache")


def yaml_safe_load(url_or_path):
    if url_or_path.startswith('http'):
        return yaml.safe_load(get_from_url(url_or_path))
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
                    if task_config['config'].get('type') == 'trigger_dag':
                        tasks[task_config['id']] = TriggerDagRunOperator(
                            task_id=task_config['id'],
                            trigger_dag_id=task_config['config']['trigger_dag_id'],
                            conf={
                                param: "{{ dag_run.conf.get('__PARAM__') }}".replace('__PARAM__', param)
                                for param
                                in task_config['config'].get('pass_conf_params', [])
                            }
                        )
                    else:
                        tasks[task_config['id']] = ApiBashOperator(
                            task_config['config'],
                            task_id=task_config['id']
                        )
                    if task_config.get('depends_on'):
                        for depends_on_task_id in task_config['depends_on']:
                            tasks[task_config['id']].set_upstream(tasks[depends_on_task_id])
                yield dag_config['name'].replace('-', '_'), dag
