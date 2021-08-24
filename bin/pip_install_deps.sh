#!/usr/bin/env bash

REPO_NAME=hasadna/open-bus-pipelines
BRANCH_NAME="${OPENBUS_PIPELINES_BRANCH:-main}"
USE_LATEST_TAG="${OPENBUS_PIPELINES_USE_LATEST_TAG:-no}"
OLD_COMMIT_FILENAME="${STRIDE_VENV}/open_bus_pipelines_commit.txt"

if [ "${USE_LATEST_TAG}" == "yes" ]; then
  NEW_COMMIT="$(curl -fs https://api.github.com/repos/${REPO_NAME}/releases/latest | jq -r .tag_name)"
else
  NEW_COMMIT="$(curl -fs https://api.github.com/repos/${REPO_NAME}/branches/${BRANCH_NAME} | jq -r .commit.sha)"
fi
if expr length "${NEW_COMMIT}" '>' 5; then
  HAS_NEW_COMMIT="yes"
else
  HAS_NEW_COMMIT="no"
fi
if [ -e "${OLD_COMMIT_FILENAME}" ]; then
  OLD_COMMIT="$(cat "${OLD_COMMIT_FILENAME}")"
  if expr length "${OLD_COMMIT}" '>' 5; then
    HAS_OLD_COMMIT="yes"
  else
    HAS_OLD_COMMIT="no"
  fi
else
  HAS_OLD_COMMIT="no"
fi
if [ "${HAS_OLD_COMMIT}" == "no" ] || [ "${HAS_NEW_COMMIT}" == "no" ] || [ "${OLD_COMMIT}" != "${NEW_COMMIT}" ]; then
  echo Updating open-bus-pipelines dependencies to ${NEW_COMMIT}... &&\
  "${STRIDE_VENV}/bin/pip" install -qqr https://raw.githubusercontent.com/hasadna/open-bus-pipelines/main/requirements-siri-etl.txt &&\
  "${STRIDE_VENV}/bin/pip" install -qqr https://raw.githubusercontent.com/hasadna/open-bus-pipelines/main/requirements-stride-etl.txt &&\
  "${STRIDE_VENV}/bin/pip" install -qqr https://raw.githubusercontent.com/hasadna/open-bus-pipelines/main/requirements-gtfs-etl.txt &&\
  if [ "${HAS_NEW_COMMIT}" == "yes" ]; then
    echo "${NEW_COMMIT}" > "${OLD_COMMIT_FILENAME}"
  fi &&\
  echo OK
else
  echo "Using existing open-bus-pipelines dependencies: ${OLD_COMMIT}"
fi
