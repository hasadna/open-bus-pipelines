# Pulled April 26, 2021
FROM python:3.8@sha256:ff2d0720243a476aae42e4594527661b3647c98cbf5c1735e2bb0311374521f4
RUN apt-get update && apt-get install -y --no-install-recommends freetds-bin \
        ldap-utils libffi6 libsasl2-2 libsasl2-modules libssl1.1 \
        locales lsb-release sasl2-bin sqlite3 unixodbc brotli
WORKDIR /srv
COPY bin/pip_install_airflow.sh bin/pip_install_airflow.sh
RUN pip install --upgrade pip && bin/pip_install_airflow.sh && rm -rf bin
COPY requirements-siri-etl.txt ./
RUN python3.8 -m venv /usr/local/lib/stride && /usr/local/lib/stride/bin/pip install -r requirements-siri-etl.txt
COPY dags/ dags/
COPY open_bus_pipelines/ open_bus_pipelines/
COPY setup.py ./
RUN pip install -e .

ENV AIRFLOW_HOME=/var/airflow
ENV AIRFLOW__CORE__DAGS_FOLDER=/srv/dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://postgres:123456@airflow-db
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__PARALLELISM=4
ENV AIRFLOW__CORE__DAG_CONCURRENCY=1
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
ENV AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=1
ENV STRIDE_VENV=/usr/local/lib/stride
ENV OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS=no
ENV OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS=yes

COPY entrypoint.sh ./
ENTRYPOINT ["/srv/entrypoint.sh"]
