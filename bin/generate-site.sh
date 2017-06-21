#!/bin/bash

set -exo pipefail

docker run --rm --user $(id -u) -v "$(pwd):/app" "$( bin/docker-image-tag.sh )"
