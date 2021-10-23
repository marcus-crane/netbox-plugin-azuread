NETBOX_VER=3.0.0

COMPOSE_FILE=./develop/docker-compose.yml
BUILD_NAME=netbox_plugin_azuread
TESTCAFE_FOLDER=e2e
TESTCAFE_ARGS=firefox "/tests/*.js"

up:
	@echo "Starting Netbox"
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d

down:
	@echo "Stopping Netbox"
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down

build:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} build --build-arg NETBOX_VER=${NETBOX_VER}

test:
	docker pull testcafe/testcafe
	docker run -it --net=host --mount type=bind,source=$(shell pwd)/${TESTCAFE_FOLDER},target=/tests testcafe/testcafe ${TESTCAFE_ARGS}