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
        kwargs['bash_command'] = '{print_dag_run}{pip_install_deps}{STRIDE_VENV}/bin/{cmd}'.format(
            STRIDE_VENV=STRIDE_VENV,
            cmd=cmd,
            print_dag_run=get_print_dag_run(),
            pip_install_deps=get_pip_install_deps()
        )
        if OPEN_BUS_PIPELINES_ALERT_EMAILS:
            kwargs['email'] = OPEN_BUS_PIPELINES_ALERT_EMAILS
        super(CliBashOperator, self).__init__(**kwargs)
