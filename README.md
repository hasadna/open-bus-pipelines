# Open Bus Pipelines

Central repository for open bus pipelines, combines all the sub-repositories together.

Includes an airflow server which manages the Open Bus project's processing pipelines
as well as a Docker Compose environment for all the different open bus components.

The actual processing is implemented in other repositories, this project only 
defines how / when to run the different processing jobs and the dependencies 
between the jobs. All the jobs run on the same server (the one where airflow scheduler runs)
but use a different Python interpreter which supports updating the job's code 
without restarting the Airflow server.

## Docker Compose environment

This is the easiest option to run all the pipeline components for local development / testing

### stride-db

Pull the latest stride-db-init image (this container handles the migrations):

```
docker-compose pull stride-db-init
```

Start the database and run all migrations:

```
docker-compose up -d stride-db-init
```

Additional functionality:
* Check migrations log: `docker-compose logs stride-db-init`
* Delete the DB data:
    * Stop the environment: `docker-compose down`
    * Delete the DB volume: `docker volume rm open-bus-pipelines_stride-db`
* Develop stride-db migrations from a local clone of stride-db:
    * Clone [hasadna/open-bus-stride-db](https://github.com/hasadna/open-bus-stride-db) to `../open-bus-stride-db` (relative to open-bus-pipelines repository)
    * Start a bash shell in the stride-db-init container: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run --entrypoint bash stride-db-init`
        * Create a migration: `alembic revision --autogenerate -m "describe the change here"`
        * Run migrations: `alembic upgrade head`
    * Build the db migrations Docker image: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml build stride-db-init`

### stride-etl

Pull the latest stride-etl image:

```
docker-compose pull stride-etl
```

See help message for available stride-etl commands:

```
docker-compose run stride-etl
```

Run a command:

```
docker-compose run stride-etl stats collect
```

Additional functionality:
* Develop stride-etl from a local clone:
    * Clone [hasadna/open-bus-stride-db](https://github.com/hasadna/open-bus-stride-db) to ../open-bus-stride-db (relative to open-bus-pipelines repository) 
    * Clone [hasadna/open-bus-stride-etl](https://github.com/hasadna/open-bus-stride-etl) to ../open-bus-stride-etl (relative to open-bus-pipelines repository)
    * Run a command: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run stride-etl stats collect`
    * Build the Docker image: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml build stride-etl`

### siri-requester

Set the following in `.env` file (see [hasadna/open-bus-siri-requester](https://github.com/hasadna/open-bus-siri-requester) for details):

```
OPEN_BUS_MOT_KEY=
OPEN_BUS_SSH_TUNNEL_SERVER_IP=
OPEN_BUS_S3_ENDPOINT_URL=
OPEN_BUS_S3_ACCESS_KEY_ID=
OPEN_BUS_S3_SECRET_ACCESS_KEY=
OPEN_BUS_S3_BUCKET=
```

Save the ssh tunnel private key file in `.data/siri-requester-key/open-bus-ssh-tunnel-private-key-file`

Pull latest siri-requester image:

```
docker-compose pull siri-requester
```

Start siri-requester daemon:

```
docker-compose up -d siri-requester
```

Additional functionality:
* Check the logs: `docker-compose logs siri-requester`
* Run siri-requester commands: `docker-compose run --entrypoint open-bus-siri-requester siri-requester --help`
* Develop siri-requester from a local clone:
    * Clone [hasadna/open-bus-siri-requester](https://github.com/hasadna/open-bus-siri-requester) to ../open-bus-siri-requester (relative to open-bus-pipelines repository) 
    * Run the siri-requester daemon: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml up -d siri-requester`
    * Run siri-requester commands: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run --entrypoint open-bus-siri-requester siri-requester --help`
    * Build the Docker image: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml build siri-requester`

### siri-etl-process-new-snapshots

Set the following in`.env` file (see [hasadna/open-bus-siri-etl](https://github.com/hasadna/open-bus-siri-etl) for details):

```
REMOTE_URL_HTTPAUTH=
```

Pull latest siri-etl image:

```
docker-compose pull siri-etl-process-new-snapshots
```

Start the siri-etl process new snapshots daemon:

```
docker-compose up -d siri-etl-process-new-snapshots
```

Additional functionality:
* Check the logs: `docker-compose logs siri-etl-process-new-snapshots`
* Run siri-etl commands: `docker-compose run --entrypoint open-bus-siri-etl siri-etl-process-new-snapshots --help`
* Develop siri-etl from a local clone:
    * Clone [hasadna/open-bus-siri-etl](https://github.com/hasadna/open-bus-siri-etl) to ../open-bus-siri-etl (relative to open-bus-pipelines repository) 
    * Run the siri-etl daemon: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml up -d siri-etl-process-new-snapshots`
    * Run siri-etl commands: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run --entrypoint open-bus-siri-etl siri-etl-process-new-snapshots --help`
    * Build the Docker image: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml build siri-etl-process-new-snapshots`

### airflow

Set the following in`.env` file (see [hasadna/open-bus-siri-etl](https://github.com/hasadna/open-bus-siri-etl) for details):

```
REMOTE_URL_HTTPAUTH=
```

Pull latest airflow image:

```
docker-compose pull airflow-scheduler
```

Start the Airflow servers:

```
docker-compose up -d airflow-scheduler
```

Login to the Airflow server at http://localhost:8080 with username/password `admin`/`123456`

Additional functionality:
* Check the scheduler logs: `docker-compose logs airflow-scheduler`
* Build the docker image: `docker-compose build airflow-scheduler`
* Local development of the airflow server (`dags/` and `open_bus_pipelines/`) is already available
* Local development of related components is not supported (you have to publish the changes to the other repositories for them to take effect)

## Local development

This allows you to run the Airflow server locally for development, it's not necessary for common development / testing requirements.

Prerequisites:

* System dependencies: https://airflow.apache.org/docs/apache-airflow/stable/installation.html#system-dependencies
* Python 3.8

Create airflow virtualenv

```
python3.8 -m venv venv/airflow
```

Install airflow and dependencies

```
. venv/airflow/bin/activate &&\
pip install --upgrade pip &&\
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
( . venv/stride/bin/activate && pip install --upgrade pip && cd ../open-bus-siri-etl && pip install -r requirements-dev.txt )
```

Install open-bus-stride-etl, assuming it's in a sibling directory you can use the following command:

```
venv/stride/bin/pip install -r ../open-bus-stride-etl/requirements.txt &&\
venv/stride/bin/pip install -e ../open-bus-stride-etl
```

Create a file at `.airflow.env` with the following contents:

```
. venv/airflow/bin/activate
export AIRFLOW_HOME=$(pwd)/.airflow
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
export AIRFLOW__CORE__DAG_DISCOVERY_SAFE_MODE=False

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
