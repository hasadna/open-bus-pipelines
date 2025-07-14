# Open Bus Pipelines

Central repository for open bus processing pipelines.

* Please report issues and feature requests [here](https://github.com/hasadna/open-bus/issues/new)
* To get updates about the system status and for general help join Hasadna's Slack #open-bus channel ([Hasadna Slack signup link](https://join.slack.com/t/hasadna/shared_invite/zt-167h764cg-J18ZcY1odoitq978IyMMig))
* See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to open-bus pipelines / stride projects.
* See [docs/](docs/) for additional documentation.

## High-level architecture

* [stride-db](https://github.com/hasadna/open-bus-stride-db):
  The database contains all the project's data.
  [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/) is used to define the
  database tables and run queries.
  [Alembic](https://alembic.sqlalchemy.org/) is used to update the database
  structure.
* [stride-etl](https://github.com/hasadna/open-bus-stride-etl):
  Data enrichment ETL / processing jobs. New processing jobs should be added here
  to enrich the core data. Processing jobs defined here are triggered from the
  Airflow server.
* [gtfs-etl](https://github.com/hasadna/open-bus-gtfs-etl):
  GTFS ETL / processing jobs - loads the GTFS data from MOT to the DB.
* [siri-requester](https://github.com/hasadna/open-bus-siri-requester):
  A daemon which continuously downloads SIRI snapshot data from the MOT servers.
* [siri-etl](https://github.com/hasadna/open-bus-siri-etl):
  A daemon which processes new SIRI snapshots downloaded by siri-requester and
  updates their data in the stride-db.
* [stride-api](https://github.com/hasadna/open-bus-stride-api):
  REST API, available at https://open-bus-stride-api.hasadna.org.il/docs
* Airflow (this repository): triggers all the project's processing pipelines.
  Each repository which contains processing jobs has an airflow.yaml file which
  defines the pipelines to run, their schedule and their arguments. All the jobs
  run on the same airflow scheduler but use a different Python interpreter which
  supports updating the job's code without restarting the Airflow server.

## Docker Compose environment

This is the easiest option to run all the pipeline components for local development / testing

### stride-db

Pull the latest stride-db-init image (this container handles the migrations or restoring from backup):

```
docker-compose pull stride-db-init
```

There are two options for initializing the DB:

* Initialize an empty DB and run all migrations:
  * (If you previously restored DB from URL, remove DB_RESTORE_FROM_URL from the .env file)
  * Run the DB and run migrations: `docker-compose up -d stride-db-init`
  * You will now have an empty DB, to get some data you should run the following commands:
    * (refer to other sections of this doc for more info and options for each command)
    * Pull images: `docker-compose pull siri-etl-process-new-snapshots stride-etl`
    * Choose a snapshot to download from https://open-bus-siri-requester.hasadna.org.il/2025/
    * Download and process the snapshot:
      * `docker-compose run --entrypoint open-bus-siri-etl siri-etl-process-new-snapshots process-snapshot --download 2025/11/27/10/00`
    * Run additional ETL processes, e.g.:
      * `docker-compose run stride-etl siri add-ride-durations`
* Restore the DB from the last production backup (will take a while and require a lot of RAM..):
  * Create a `.env` file in current directory with the following contents:
    ```
    DB_RESTORE_FROM_URL=yes
    ```
  * Make sure you have an empty DB by running: `docker-compose down -v`
  * Restore the DB: `docker-compose up -d stride-db-init`
  * Wait, it will take a while, you can track progress by running `docker-compose logs -f stride-db-init`

You can now connect to the DB locally using any PostgreSQL client on:
* host: `localhost`
* port: `5432`
* username: `postgres`
* password: `123456`
* db: `postgres` 

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

### gtfs-etl

Pull the latest gtfs-etl image:

```
docker-compose pull gtfs-etl
```

See help message for available gtfs-etl commands:

```
docker-compose run gtfs-etl
```

Additional functionality:
* Develop gtfs-etl from a local clone:
    * Clone [hasadna/open-bus-stride-db](https://github.com/hasadna/open-bus-stride-db) to ../open-bus-stride-db (relative to open-bus-pipelines repository) 
    * Clone [hasadna/open-bus-gtfs-etl](https://github.com/hasadna/open-bus-gtfs-etl) to ../open-bus-gtfs-etl (relative to open-bus-pipelines repository)
    * Run a command: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run gtfs-etl --help`
    * Build the Docker image: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml build gtfs-etl`

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

Pull latest siri-requester images:

```
docker-compose pull siri-requester siri-requester-nginx
```

Start siri-requester daemon:

```
docker-compose up -d siri-requester
```

Additional functionality:
* Check the logs: `docker-compose logs siri-requester`
* Run siri-requester commands: `docker-compose run --entrypoint open-bus-siri-requester siri-requester --help`
* Run the siri-requester health-check daemon and nginx: `docker-compose up -d siri-requester-nginx`
* Develop siri-requester from a local clone:
    * Clone [hasadna/open-bus-siri-requester](https://github.com/hasadna/open-bus-siri-requester) to ../open-bus-siri-requester (relative to open-bus-pipelines repository) 
    * Run the siri-requester daemon: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml up -d siri-requester`
    * Run siri-requester healthcheck and nginx: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml up -d siri-requester-nginx`
    * Run siri-requester commands: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run --entrypoint open-bus-siri-requester siri-requester --help`
    * Build the Docker images: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml build siri-requester siri-requester-nginx`
    * Run unit tests:
        * Start a bash shell: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run --entrypoint bash siri-requester`
            * Install test requirements: `pip install -r tests/requirements.txt`
            * Run tests: `pytest -svvx`

### siri-etl-process-new-snapshots

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
    * Run unit tests:
        * Start a fresh stride-db: `docker-compose down; docker volume rm open-bus-pipelines_stride-db; docker-compose up -d stride-db-init`
        * Start a bash shell: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml run --entrypoint bash siri-etl-process-new-snapshots`
            * Install test requirements: `pip install -r tests/requirements.txt`
            * Run tests: `pytest -svvx`

### stride-api

Pull latest stride-api image:

```
docker-compose pull stride-api
```

Start the stride-api server:

```
docker-compose up -d stride-api
```

Access at http://localhost:8000/docs

Additional functionality:
* Check the logs: `docker-compose logs stride-api`
* Develop stride-api from a local clone:
    * Clone [hasadna/open-bus-stride-api](https://github.com/hasadna/open-bus-stride-api) to ../open-bus-stride-api (relative to open-bus-pipelines repository) 
    * Run the stride-api server: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml up -d stride-api`
    * Build the Docker image: `docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml build stride-api`

### airflow

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
* [uv](https://docs.astral.sh/uv/getting-started/installation/)

Install airflow and dependencies

```
uv sync
uv pip install --upgrade pip &&\
uv run bin/pip_install_airflow.sh &&\
uv pip install -e . &&\
uv pip install -r tests/requirements.txt
```

Create stride virtualenv:

```
uv venv .venv/stride
uv pip install --upgrade pip --no-config --python .venv/stride/bin/python
```

Follow the [open-bus-siri-etl README](https://github.com/hasadna/open-bus-siri-etl/blob/main/README.md) for local installation on this virtualenv.
You can try the following one-liner if you already have all the required dependencies and repositories:

```
( . .venv/stride/bin/activate && pip install --upgrade pip && cd ../open-bus-siri-etl && pip install -r requirements-dev.txt )
```

Install open-bus-stride-etl, assuming it's in a sibling directory you can use the following command:

```
.venv/stride/bin/pip install -r ../open-bus-stride-etl/requirements.txt &&\
.venv/stride/bin/pip install -e ../open-bus-stride-etl
```

Install open-bus-gtfs-etl, assuming it's in a sibling directory you can use the following command:

```
.venv/stride/bin/pip install -r ../open-bus-gtfs-etl/requirements.txt &&\
.venv/stride/bin/pip install -e ../open-bus-gtfs-etl
```

Create a file at `.airflow.env` with the following contents:

```
. .venv/airflow/bin/activate
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
export SQLALCHEMY_URL=postgresql://postgres:123456@localhost
export DEBUG=yes
```

Create directory for airflow data:

```
sudo mkdir /var/airflow
sudo chown $USER /var/airflow
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

### Testing local development with parallel workers

This process is a bit more complex but allows to test workflows which require airflow workers to run in parallel.

Add the following to the end of `.airflow.env`:

```
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://postgres:123456@localhost:5433
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__CORE__PARALLELISM=4
export AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=3
```

Start the airflow db

```
docker compose up -d airflow-db
```

Start the airflow webserver / scheduler as described above, including the db initialization and admin user creation.
