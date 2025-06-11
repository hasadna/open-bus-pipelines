import os
import time
import json
import hashlib
import datetime
import traceback

import requests
from ruamel import yaml


CACHE_PATH = '/var/airflow/open-bus-pipelines-dags-cache'


def get_from_url(url):
    cache_key = hashlib.sha256(url.encode()).hexdigest()
    cache_filename = os.path.join(CACHE_PATH, cache_key + '.json')
    os.makedirs(CACHE_PATH, exist_ok=True)
    res = None
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        res = response.text
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
