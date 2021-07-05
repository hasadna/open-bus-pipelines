#!/usr/bin/env bash

if [ "${OPEN_BUS_PIPELINES_AIRFLOW_INITIALIZE}" == "yes" ]; then
  if [ -f "${AIRFLOW_HOME}/airflow.cfg" ]; then
    airflow db upgrade
  else
    airflow db init
  fi &&\
  if ! airflow users list | grep Adminski; then
    airflow users create --username admin --firstname Admin --lastname Adminski \
      --role Admin --password "${OPEN_BUS_PIPELINES_AIRFLOW_ADMIN_PASSWORD}" --email admin@localhost
  fi
fi &&\
if [ "${OPEN_BUS_PIPELINES_AIRFLOW_ROLE}" == "webserver" ]; then
  rm -f "${AIRFLOW_HOME}/airflow-webserver.pid" &&\
  exec airflow webserver --port 8080
elif [ "${OPEN_BUS_PIPELINES_AIRFLOW_ROLE}" == "scheduler" ]; then
  exec airflow scheduler
else
  exit 1
fi