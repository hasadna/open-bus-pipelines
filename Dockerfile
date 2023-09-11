# Pulled Sep. 11, 2023
FROM --platform=linux/amd64 python:3.8@sha256:9c7e79fb6ee130af5c0be2e3dea04cb6537891e9d398b1d120586110bdc58731
RUN apt-get update && apt-get install -y --no-install-recommends freetds-bin \
        ldap-utils libffi8 libsasl2-2 libsasl2-modules libssl3 \
        locales lsb-release sasl2-bin sqlite3 unixodbc brotli jq
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" &&\
    unzip awscliv2.zip && rm awscliv2.zip &&\
    ./aws/install && aws --version
WORKDIR /srv
COPY bin/ bin/
COPY requirements.txt ./
RUN pip install --upgrade pip && bin/pip_install_airflow.sh
RUN python3.8 -m venv /usr/local/lib/stride &&\
    /usr/local/lib/stride/bin/pip install --upgrade pip
COPY webserver_config.py ./
COPY dags/ dags/
COPY open_bus_pipelines/ open_bus_pipelines/
COPY setup.py ./
RUN pip install -e .

ENV AIRFLOW_HOME=/var/airflow
ENV AIRFLOW__CORE__DAGS_FOLDER=/srv/dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://postgres:123456@airflow-db
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__PARALLELISM=4
ENV AIRFLOW__SCHEDULER__MAX_TIS_PER_QUERY=0
ENV AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=1
ENV AIRFLOW__CORE__DAG_DISCOVERY_SAFE_MODE=False
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
ENV AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=1
ENV AIRFLOW__WEBSERVER__CONFIG_FILE=/srv/webserver_config.py
ENV STRIDE_VENV=/usr/local/lib/stride
ENV OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS=no
ENV OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS=yes

COPY entrypoint.sh ./
ENTRYPOINT ["/srv/entrypoint.sh"]
