import sys
import json
import importlib


def main(config, dag_run_conf):
    print('config: {}'.format(config))
    print('dag_run_conf: {}'.format(dag_run_conf))
    config = json.loads(config)
    dag_run_conf = json.loads(dag_run_conf)
    module = importlib.import_module(config['module'])
    function = getattr(module, config['function'])
    kwargs = {}
    for kwarg_name, kwarg_conf in config.get('kwargs', {}).items():
        kwargs[kwarg_name] = dag_run_conf.get(kwarg_name, kwarg_conf.get('default'))
    if config['type'] == 'cli':
        print('invoking cli function with kwargs: {}'.format(kwargs))
        function.callback(**kwargs)
    elif config['type'] == 'api':
        print('invoking api function with kwargs: {}'.format(kwargs))
        function(**kwargs)
    else:
        raise Exception('unsupported type: {}'.format(config['type']))


if __name__ == '__main__':
    main(*sys.argv[1:])
