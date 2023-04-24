ACTIONS := $(wildcard */.)
ENVIRONMENTS := $(ACTIONS:%/.=%.zip)

.PHONY: clean

all: $(ENVIRONMENTS)

%.zip: %/main.js
	# Each action gets its own "node_modules" folder, so we build the dependencies
	# and package the action under the same target
	@echo Action: $*
	cd $* && \
		npm ci && \
		zip --quiet --recurse-paths ../$@ *

clean:
	rm -f *.zip
	rm -rf */node_modules

