FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
RUN apt update && apt install -y curl ca-certificates git &&\
    install -m 0755 -d /etc/apt/keyrings &&\
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc &&\
    chmod a+r /etc/apt/keyrings/docker.asc &&\
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" > /etc/apt/sources.list.d/docker.list &&\
    apt update && apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
RUN useradd -m -s /bin/bash agent
RUN apt update && apt install -y sudo
RUN echo 'agent ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/agent &&\
    chmod 440 /etc/sudoers.d/agent
USER agent
WORKDIR /home/agent
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ARG NVM_VERSION=0.40.3
ARG NODE_VERSION=22
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh | bash
RUN echo 'export PATH="/home/agent/.local/bin:$PATH"' > .bash_env &&\
    echo '. /home/agent/.local/bin/env' >> .bash_env &&\
    echo 'export NVM_DIR=/home/agent/.nvm' >> .bash_env &&\
    echo '. /home/agent/.nvm/nvm.sh' >> .bash_env &&\
    echo '. /home/agent/.nvm/bash_completion' >> .bash_env &&\
    echo ". /home/agent/.bash_env" >> /home/agent/.bashrc
ENV BASH_ENV=/home/agent/.bash_env
ARG PYTHON_VERSION=3.8
RUN . $BASH_ENV && uv python install ${PYTHON_VERSION}

# Setup the pipelines project
RUN git clone https://github.com/hasadna/open-bus-pipelines.git
WORKDIR /home/agent/open-bus-pipelines
# General dependency requirements
RUN sudo apt update && sudo apt install -y libpq-dev build-essential
# install airflow venv
RUN . $BASH_ENV && uv sync &&\
    uv pip install --upgrade pip &&\
    . .venv/bin/activate &&\
    bin/pip_install_airflow.sh &&\
    pip install -e . &&\
    pip install -r tests/requirements.txt
# install stride venv
RUN . $BASH_ENV && uv venv .venv/stride &&\
    uv pip install --upgrade pip --no-config --python .venv/stride/bin/python
# Clone related projects
RUN for PROJ in open-bus-siri-etl open-bus-siri-requester open-bus-stride-db; do \
      if [ -d "../${PROJ}" ]; then \
        echo "Directory ../${PROJ} already exists" &&\
        exit 1 ;\
      else \
        git clone "https://github.com/hasadna/${PROJ}.git" "../${PROJ}" ;\
      fi ;\
    done
# Install open-bus-siri-etl according to it's README
RUN . $BASH_ENV && . .venv/stride/bin/activate &&\
    sudo apt update && sudo apt install -y brotli &&\
    cd ../open-bus-siri-etl &&\
    pip install -r requirements-dev.txt &&\
    echo 'export SQLALCHEMY_URL=postgresql://postgres:123456@localhost' > .env &&\
    echo 'export DEBUG=yes' >> .env
# Install other related projects
RUN . $BASH_ENV && . .venv/stride/bin/activate &&\
    for PROJ in open-bus-stride-etl open-bus-gtfs-etl; do \
      git clone "https://github.com/hasadna/${PROJ}.git" "../${PROJ}" &&\
      cd "../${PROJ}" &&\
      pip install -r requirements.txt &&\
      pip install -e . ;\
    done
# Airflow Initialization
RUN echo ". .venv/bin/activate" > .airflow.env &&\
    echo "export AIRFLOW_HOME=$(pwd)/.airflow" >> .airflow.env &&\
    echo "export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags" >> .airflow.env &&\
    echo "export AIRFLOW__CORE__LOAD_EXAMPLES=False" >> .airflow.env &&\
    echo "export AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False" >> .airflow.env &&\
    echo "export AIRFLOW__CORE__DAG_DISCOVERY_SAFE_MODE=False" >> .airflow.env &&\
    echo "export OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS=yes" >> .airflow.env &&\
    echo "export OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS=no" >> .airflow.env &&\
    echo "export OPEN_BUS_SIRI_STORAGE_ROOTPATH=$(pwd)/.data/siri" >> .airflow.env &&\
    echo "export SQLALCHEMY_URL=postgresql://postgres:123456@localhost" >> .airflow.env &&\
    echo "export DEBUG=yes" >> .airflow.env &&\
    . $BASH_ENV && . ./.airflow.env &&\
    airflow db init &&\
    airflow users create --username admin --firstname Admin --lastname Adminski --role Admin --password 12345678 --email admin@localhost

USER root
RUN rm /etc/sudoers.d/agent
USER agent
#RUN . $BASH_ENV && npm install -g @openai/codex
#ENTRYPOINT ["codex"]
