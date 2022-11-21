import os
import sys
from textwrap import dedent

from open_bus_pipelines.yaml_loader import yaml_safe_load, get_from_url


def get_desc_markdown(desc_items, desc):
    desc = dedent(desc).strip()
    for id, url in desc_items.items():
        desc = desc.replace(f'[[{id}]]', f'[{id}]({url})')
    return desc


def get_stride_db_desc_items():
    res = {}
    md = get_from_url('https://raw.githubusercontent.com/hasadna/open-bus-stride-db/main/DATA_MODEL.md')
    for line in md.splitlines():
        if line.startswith('#') and len(line.split(' ')) == 2:
            item_id = line.split(' ')[1]
            url = f'https://github.com/hasadna/open-bus-stride-db/blob/main/DATA_MODEL.md#{item_id.replace(".", "")}'
            res[item_id] = url
    return res


def get_source_url(url, filename=None):
    if not url.startswith('https://raw.githubusercontent.com/'):
        return None
    if '/main/' not in url:
        return None
    url = url.replace('https://raw.githubusercontent.com/', 'https://www.github.com/')
    if filename:
        url = os.path.join(url, filename)
    url = '/'.join(url.split('/')[0:-1])
    url = url.replace('/main/', '/tree/main/')
    return url

def generate_markdown(filename):
    desc_items = get_stride_db_desc_items()
    markdown = '# Open Bus Stride ETL Processes\n\n'
    markdown += 'This document is generated automatically from etl process definitions.\n'
    markdown += 'Click on the process name to see the related source code.\n\n'
    dags = {}
    for url in [
        'https://raw.githubusercontent.com/hasadna/open-bus-siri-requester/main/open_bus_siri_requester/etl-docs.yaml',
        'https://raw.githubusercontent.com/hasadna/open-bus-siri-etl/main/open_bus_siri_etl/etl-docs.yaml'
    ]:
        for dag in yaml_safe_load(url):
            assert dag['name'] not in dags
            dags[dag['name']] = {
                'desc': dag['desc'],
                'source_url': get_source_url(url)
            }
            desc_items[dag['name']] = f'#{dag["name"]}'
    for etl in yaml_safe_load('./etl_index.yaml'):
        url_or_path = etl.get('url', etl.get('path'))
        assert url_or_path
        for dag_filename in yaml_safe_load(os.path.join(url_or_path, 'airflow.yaml'))['dag_files']:
            for dag in yaml_safe_load(os.path.join(url_or_path, dag_filename)):
                docs = dag.get('docs') or {}
                if not docs.get('hide'):
                    assert dag['name'] not in dags
                    dags[dag['name']] = {
                        'desc': docs.get('desc', dag.get('description')),
                        'source_url': get_source_url(url_or_path, dag_filename)
                    }
                    desc_items[dag['name']] = f'#{dag["name"]}'
    for dag_name, dag in dags.items():
        if dag.get('source_url'):
            markdown += f'## [{dag_name}]({dag["source_url"]})\n\n'
        else:
            markdown += f'## {dag_name}\n\n'
        markdown += f'{get_desc_markdown(desc_items, dag["desc"])}\n\n'
    with open(filename, 'w') as f:
        f.write(markdown)


generate_markdown(os.path.join(sys.argv[1], 'STRIDE_ETL_PROCESSES.md'))
