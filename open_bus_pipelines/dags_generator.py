from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from open_bus_pipelines.operators.api_bash_operator import ApiBashOperator
from open_bus_pipelines.yaml_loader import yaml_safe_load
from open_bus_pipelines.sensors.dag_time_exceeded_sensor import DagTimeExceededSensor


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
                dag_id=dag_config['name'],
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
                            config=task_config['config'],
                            task_id=task_config['id']
                        )
                    if task_config.get('depends_on'):
                        for depends_on_task_id in task_config['depends_on']:
                            tasks[task_config['id']].set_upstream(tasks[depends_on_task_id])
                if not dag_config.get('disable_alert_after_minutes'):
                    DagTimeExceededSensor(
                        alert_after_minutes=dag_config.get('alert_after_minutes') or 360,
                        task_id='monitor_task', mode='reschedule', poke_interval=60
                    )
                yield dag_config['name'].replace('-', '_'), dag
