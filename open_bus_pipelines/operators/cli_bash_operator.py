import os
import tempfile
import requests

from airflow.operators.bash import BashOperator

from open_bus_pipelines.config import STRIDE_VENV, OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS, OPEN_BUS_PIPELINES_ROOTDIR


def get_pip_install_deps():
    if not OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS:
        return ''
    with tempfile.TemporaryDirectory() as tempdir:
        tempfilename = os.path.join(tempdir, 'requirements.txt')
        with open(tempfilename, 'w') as f:
            for filename in ['requirements-siri-etl.txt', 'requirements-stride-etl.txt', 'requirements-gtfs-etl.txt']:
                f.write('# {}'.format(filename))
                f.write(requests.get('https://raw.githubusercontent.com/hasadna/open-bus-pipelines/main/{}'.format(filename)).text)
                f.write("\n")
        with open(tempfilename) as f:
            print(f.read())
        return '{}/bin/pip install -qqr {} && '.format(STRIDE_VENV, tempfilename)


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
        super(CliBashOperator, self).__init__(**kwargs)
