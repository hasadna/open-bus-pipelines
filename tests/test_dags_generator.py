from pathlib import Path

from open_bus_pipelines.dags_generator import dags_generator
from open_bus_pipelines.operators.api_bash_operator import ApiBashOperator
from open_bus_pipelines import config
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


def write_yaml(path: Path, text: str):
    path.write_text(text)


def test_basic_dag_generation(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "OPEN_BUS_PIPELINES_ALERT_EMAILS", [])

    write_yaml(tmp_path / "airflow.yaml", "dag_files:\n  - dags.yaml\n")
    dags_yaml = """
- name: my-dag
  schedule_interval: '@daily'
  tasks:
    - id: first
      config:
        type: api
    - id: second
      config:
        type: trigger_dag
        trigger_dag_id: other
        pass_conf_params: [foo]
      depends_on:
        - first
"""
    write_yaml(tmp_path / "dags.yaml", dags_yaml)

    dags = list(dags_generator(str(tmp_path) + "/"))
    assert len(dags) == 1
    dag_id, dag = dags[0]
    assert dag_id == "my_dag"

    assert set(dag.task_dict.keys()) == {"first", "second", "monitor_task"}
    assert isinstance(dag.get_task("first"), ApiBashOperator)
    second = dag.get_task("second")
    assert isinstance(second, TriggerDagRunOperator)
    assert second.conf == {"foo": "{{ dag_run.conf.get('foo') }}"}
    assert "first" in second.upstream_task_ids


def test_disable_alert(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "OPEN_BUS_PIPELINES_ALERT_EMAILS", [])
    write_yaml(tmp_path / "airflow.yaml", "dag_files:\n  - d.yaml\n")
    dags_yaml = """
- name: no-alert-dag
  disable_alert_after_minutes: true
  tasks:
    - id: t
      config:
        type: api
"""
    write_yaml(tmp_path / "d.yaml", dags_yaml)
    dags = list(dags_generator(str(tmp_path) + "/"))
    dag_id, dag = dags[0]
    assert dag_id == "no_alert_dag"
    assert set(dag.task_dict.keys()) == {"t"}
