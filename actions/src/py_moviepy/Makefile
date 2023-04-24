# Name of the virtualenv directory built with the dependency
# It is better to keep it as a hidden folder because this Makefile gets the list
# of actions to build by listing all folders
# Note that in the final bundle, the directory *must* be named "virtualenv"
VIRTUALENV = .virtualenv
# Name of the Docker container runtime image
DOCKER_IMAGE = python3action
# Tag of the Docker container runtime image
DOCKER_TAG = moviepy

ACTIONS := $(wildcard */.)
ENVIRONMENTS := $(ACTIONS:%/.=%.zip)

.PHONY: clean

all: $(ENVIRONMENTS)

# Build the Docker runtime image with system dependencies
.runtime: Dockerfile
	# Trick to avoid sending the "context" to the Docker daemon
	cat Dockerfile | docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -
	touch .runtime

# Get UID/GID of current user to fix owernship of built virtualenv folder
# (commands are run as root inside the container, so the folder would end up
# being owned by root).
UID := $(shell id -u)
GID := $(shell id -g)

# Build the Python virtualenv with Python dependencies from PyPI
$(VIRTUALENV): requirements.txt
	docker run --rm -v "$(CURDIR):/tmp" openwhisk/python3action bash -c \
		"cd /tmp && \
	    	virtualenv $(VIRTUALENV) && \
			source $(VIRTUALENV)/bin/activate && \
			pip install -r requirements.txt && \
			chown $(UID):$(GID) -R $(VIRTUALENV)"

%.zip: %/__main__.py .runtime $(VIRTUALENV)
	@echo Action: $*
	# make a temporary symbolic link to the virtualenv so its get its proper name
	# hardcoded by Openwhisk: "virtualenv"
	ln -s $(VIRTUALENV) virtualenv
	zip --quiet --recurse-paths $@ virtualenv
	zip --quiet --recurse-paths --junk-paths $@ $*/*
	unlink virtualenv

clean:
	docker rmi -f $(DOCKER_IMAGE):$(DOCKER_TAG)
	rm -f .runtime
	rm -rf $(VIRTUALENV)
	rm -f *.zip


