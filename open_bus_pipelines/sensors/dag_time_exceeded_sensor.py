from datetime import datetime, timedelta

from airflow.sensors.base import BaseSensorOperator
from airflow.models import DagRun, TaskInstance
from airflow.utils.db import provide_session
from airflow.utils.state import TaskInstanceState


class DagTimeExceededSensor(BaseSensorOperator):

    def __init__(self, *args, alert_after_minutes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.alert_after_minutes = alert_after_minutes

    def is_dag_running_too_long(self, session, current_dag_run_id):
        current_dag_run = session.query(DagRun).filter(
            DagRun.dag_id == self.dag_id,
            DagRun.run_id == current_dag_run_id
        ).first()
        if current_dag_run and current_dag_run.start_date:
            duration = datetime.utcnow() - current_dag_run.start_date.replace(tzinfo=None)
            if duration > timedelta(minutes=int(self.alert_after_minutes)):
                return True
        return False

    def is_all_other_tasks_complete(self, session, current_dag_run_id):
        task_instances = session.query(TaskInstance).filter(
            TaskInstance.dag_id == self.dag_id,
            TaskInstance.run_id == current_dag_run_id,
            TaskInstance.task_id != self.task_id,
        ).all()
        all_other_tasks_complete = all(ti.state in {TaskInstanceState.SUCCESS, TaskInstanceState.FAILED, TaskInstanceState.SKIPPED, TaskInstanceState.REMOVED} for ti in task_instances)
        return all_other_tasks_complete

    @provide_session
    def poke(self, context, session=None):
        if not self.alert_after_minutes:
            self.log.info("alert_after_minutes not set, skipping")
            return True
        current_dag_run_id = context['dag_run'].run_id
        if self.is_all_other_tasks_complete(session, current_dag_run_id):
            self.log.info("All other tasks have completed")
            return True
        if self.is_dag_running_too_long(session, current_dag_run_id):
            raise Exception(f"DAG running for too long (more than {self.alert_after_minutes} minutes)")
        self.log.info("Waiting for other tasks to complete or timeout...")
        return False
