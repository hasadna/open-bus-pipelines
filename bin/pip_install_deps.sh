#!/usr/bin/env bash

# lock will be released when script exits
exec 8>/var/lock/pip_install_deps
echo waiting for lock
if ! flock -w 300 -x 8; then
  echo failed to get lock
  exit 1
fi
echo lock acquired

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
  "${STRIDE_VENV}/bin/pip" install -qqr "https://raw.githubusercontent.com/hasadna/open-bus-pipelines/${NEW_COMMIT}/requirements-siri-etl.txt" &&\
  "${STRIDE_VENV}/bin/pip" install -qqr "https://raw.githubusercontent.com/hasadna/open-bus-pipelines/${NEW_COMMIT}/requirements-stride-etl.txt" &&\
  "${STRIDE_VENV}/bin/pip" install -qqr "https://raw.githubusercontent.com/hasadna/open-bus-pipelines/${NEW_COMMIT}/requirements-gtfs-etl.txt" &&\
  if [ "${HAS_NEW_COMMIT}" == "yes" ]; then
    echo "${NEW_COMMIT}" > "${OLD_COMMIT_FILENAME}"
  fi &&\
  echo OK
else
  echo "Using existing open-bus-pipelines dependencies: ${OLD_COMMIT}"
fi

echo releasing lock
exec 8>&-
rm -f /var/lock/pip_install_deps
echo lock released
