# Open Bus Pipelines

An airflow server which manages the Open Bus project's processing pipelines.

The actual processing is implemented in other repositories, this project only 
defines how / when to run the different processing jobs and the dependencies 
between the jobs.

All the jobs run on the same server (the one where airflow scheduler runs)
but use a different Python interpreter which supports updating the job's code 
without restarting the Airflow server.

## Docker Compose environment

This is the easiest option to run the Airflow server for local development / testing

Create a `.env` file with the secret values:

```
REMOTE_URL_HTTPAUTH=username:password
```

Pull latest stride-db image:

```
docker pull docker.pkg.github.com/hasadna/open-bus-stride-db/open-bus-stride-db:latest
```

Start the docker compose environment:

```
docker-compose up -d --build
```

## Local development

This allows you to run the Airflow server locally for development, it's not necessary for common development / testing requirements.

Prerequisites:

* System dependencies: https://airflow.apache.org/docs/apache-airflow/stable/installation.html#system-dependencies
* Python 3.8

Create and install airflow virtualenv and dependencies

```
python3.8 -m venv venv/airflow &&\
. venv/airflow/bin/activate &&\
bin/pip_install_airflow.sh &&\
pip install -e .
```

Create stride virtualenv:

```
python3.8 -m venv venv/stride
```

Follow the [open-bus-siri-etl README](https://github.com/hasadna/open-bus-siri-etl/blob/main/README.md) for local installation on this virtualenv.
You can try the following one-liner if you already have all the required dependencies and repositories:

```
( . venv/stride/bin/activate && cd ../open-bus-siri-etl && pip install -r requirements-dev.txt )
```

Create a file at `.airflow.env` with the following contents:

```
. venv/airflow/bin/activate
export AIRFLOW_HOME=$(pwd)/.airflow
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False

export OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS=yes
export OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS=no
```

Add environment variables for SIRI ETL (See the [README](https://github.com/hasadna/open-bus-siri-etl/blob/main/README.md) for more details):

```
export OPEN_BUS_SIRI_STORAGE_ROOTPATH=$(pwd)/.data/siri
export REMOTE_URL_HTTPAUTH=username:password
export SQLALCHEMY_URL=postgresql://postgres:123456@localhost
export DEBUG=yes
```

Initialize the Airflow DB and create an admin user:

```
. .airflow.env &&\
airflow db init &&\
airflow users create --username admin --firstname Admin --lastname Adminski \
    --role Admin --password 12345678 --email admin@localhost
```

Start the stride local DB server and update to latest migration (see the [open-bus-stride-db README](https://github.com/hasadna/open-bus-stride-db/blob/main/README.md))

Start the Airflow web server:

```
. .airflow.env && airflow webserver --port 8080
```

In a new terminal, start the Airflow scheduler:

```
. .airflow.env && airflow scheduler
```

Access the airflow webserver at http://localhost:8080 login using admin / 12345678
