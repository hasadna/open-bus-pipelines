#!/usr/bin/env bash

# script to setup environment for AI agents

set -euo pipefail

# install airflow venv

uv sync
uv pip install --upgrade pip
. .venv/bin/activate
bin/pip_install_airflow.sh
pip install -e .
pip install -r tests/requirements.txt

# install stride venv

uv venv .venv/stride
uv pip install --upgrade pip --no-config --python .venv/stride/bin/python
. .venv/stride/bin/activate

# Clone related projects
for PROJ in open-bus-siri-etl open-bus-siri-requester open-bus-stride-db; do
  if [ -d "../${PROJ}" ]; then
    echo "Directory ../${PROJ} already exists"
    exit 1
  else
    git clone --depth 1 "https://github.com/hasadna/${PROJ}.git" "../${PROJ}"
  fi
done

# Install open-bus-siri-etl according to it's README
apt update && apt install -y brotli
(
  cd ../open-bus-siri-etl
  pip install -r requirements-dev.txt
  echo 'export SQLALCHEMY_URL=postgresql://postgres:123456@localhost' > .env
  echo 'export DEBUG=yes' >> .env
)

# Install other related projects
for PROJ in open-bus-stride-etl open-bus-gtfs-etl; done
  (
    if [ -d "../${PROJ}" ]; then
      echo "Directory ../${PROJ} already exists"
      exit 1
    else
      git clone --depth 1 "https://github.com/hasadna/${PROJ}.git" "../${PROJ}"
    fi
    cd "../${PROJ}"
    pip install -r requirements.txt
    pip install -e .
  )
done

# Airflow Initialization

echo "
. .venv/bin/activate
export AIRFLOW_HOME=$(pwd)/.airflow
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
export AIRFLOW__CORE__DAG_DISCOVERY_SAFE_MODE=False
export OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS=yes
export OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS=no
export OPEN_BUS_SIRI_STORAGE_ROOTPATH=$(pwd)/.data/siri
export SQLALCHEMY_URL=postgresql://postgres:123456@localhost
export DEBUG=yes
" > .airflow.env
sudo mkdir /var/airflow
sudo chown $USER /var/airflow
. .airflow.env
airflow db init
airflow users create --username admin --firstname Admin --lastname Adminski \
    --role Admin --password 12345678 --email admin@localhost

touch .AGENTS.sh.completed
