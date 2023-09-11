import os
import json
import shlex

from .cli_bash_operator import CliBashOperator
from ..config import OPEN_BUS_PIPELINES_ROOTDIR


class ApiBashOperator(CliBashOperator):

    def __init__(self, config, **kwargs):
        super(ApiBashOperator, self).__init__(cmd=self._get_cli_bash_operator_cmd(config), **kwargs)

    def _get_cli_bash_operator_cmd(self, config):
        return ' '.join([
            'python', '-u',
            os.path.join(OPEN_BUS_PIPELINES_ROOTDIR, 'open_bus_pipelines', 'operators', '_api_bash_operator_script.py'),
            shlex.quote(json.dumps(config)),
            '__airflow_dag_run_conf__'
        ])

    def execute(self, context):
        self.bash_command = self.bash_command.replace('__airflow_dag_run_conf__', shlex.quote(json.dumps(context['dag_run'].conf)))
        return super(ApiBashOperator, self).execute(context)
