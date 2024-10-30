from airflow.operators.bash import BashOperator

from open_bus_pipelines.config import (
    STRIDE_VENV, OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS, OPEN_BUS_PIPELINES_ROOTDIR,
    OPEN_BUS_PIPELINES_ALERT_EMAILS
)


def get_pip_install_deps():
    if not OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS:
        return ''
    return '{}/bin/pip_install_deps.sh && '.format(OPEN_BUS_PIPELINES_ROOTDIR)


def get_print_dag_run():
    return 'cat << EOF\n{{ dag_run.conf | tojson }}\nEOF\n'


class CliBashOperator(BashOperator):

    def __init__(self, cmd, **kwargs):
        assert not kwargs.get('bash_command')
        super(CliBashOperator, self).__init__(**kwargs)
        self.bash_command = '{print_dag_run}{pip_install_deps}{ENV}{STRIDE_VENV}/bin/{cmd}'.format(
            ENV=f'SQLALCHEMY_APPLICATION_NAME="{self.task_id}" SQLALCHEMY_APPLICATION_VERSION="$(cat {STRIDE_VENV}/open_bus_pipelines_commit.txt)" ',
            STRIDE_VENV=STRIDE_VENV,
            cmd=cmd,
            print_dag_run=get_print_dag_run(),
            pip_install_deps=get_pip_install_deps()
        )
        if OPEN_BUS_PIPELINES_ALERT_EMAILS:
            self.email = OPEN_BUS_PIPELINES_ALERT_EMAILS
