#!/bin/bash

set -eo pipefail

IMAGE_NAME="mfsa-site-builder"
GIT_COMMIT="${GIT_COMMIT:-$(git rev-parse HEAD)}"
echo "${IMAGE_NAME}:${GIT_COMMIT}"
