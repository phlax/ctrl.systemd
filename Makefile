#!/usr/bin/make -f

SHELL := /bin/bash


image:
	source .docker \
	   && if [ -f .env ]; then source .env; fi \
	   && docker build \
	         -t ctrl-systemd \
		 --build-arg APP_NAME="$$APP_NAME" \
		 --build-arg APP_USERNAME="$$APP_USERNAME" \
		 --build-arg BUILD_IMAGE="$$BUILD_IMAGE" \
		 --build-arg APP_ROOT="$$APP_ROOT" \
		 --build-arg EGGS="$$EGGS" \
		 --build-arg ON_CONTAINER_START="$$ON_CONTAINER_START" \
		 --build-arg BUILD_PKGS="$$BUILD_PKGS" \
		 --build-arg SYSTEM_PKGS="$$SYSTEM_PKGS" \
		 --build-arg APP_CONFIG="$$APP_CONFIG" \
		github.com/phlax/docker-app#master:context
