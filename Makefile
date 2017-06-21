GIT_COMMIT = $(shell git rev-parse HEAD)
BUILD_FILE:=.docker-$(GIT_COMMIT)

default: help
	@echo ""
	@echo "You need to specify a subcommand."
	@exit 1

help:
	@echo "build         - build the static site using docker"
	@echo "build-local   - build the static site using local environment"
	@echo "run           - run the site for dev"
	@echo "run-static    - run a web server in the static site directory"
	@echo "docker        - build the docker image"
	@echo ""
	@echo "clean         - remove all build, test, coverage and Python artifacts"
	@echo "rebuild       - force a rebuild of all of the docker images and site"

$(BUILD_FILE):
	${MAKE} docker

docker:
	bin/build-docker-image.sh
	touch $(BUILD_FILE)

build: $(BUILD_FILE)
	bin/generate-site.sh

build-local:
	generator/bin/generate.sh

rebuild: clean build

clean:
	-rm -f .docker-*
	-rm -f generator/db.sqlite3
	-rm -rf _publish
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

run: build
	bin/run-site.sh

run-static:
	cd _publish && python -m SimpleHTTPServer

.PHONY: docker build run clean rebuild run-static build-local
