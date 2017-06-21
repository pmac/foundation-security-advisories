#!/bin/bash

set -exo pipefail

DOCKER_TAG=$( bin/docker-image-tag.sh )

docker build -t "$DOCKER_TAG" .
