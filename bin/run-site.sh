#!/bin/bash

set -exo pipefail

docker run --rm -it --user $(id -u) -v "$(pwd):/app" -p 8000:8000 "$( bin/docker-image-tag.sh )" generator/bin/run.sh
