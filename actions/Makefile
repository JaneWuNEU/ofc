# Main Makefile
#
# The target "all" will build all action runtime targets, i.e. all subfolders
# of "src". It delegates building the actions of an action runtime to specific
# Makefiles found in the action runtime subfolders.
#
# The last step is to gather the built actions by copying the Zip archives built by
# the specific Makefiles to the directory "OUTPUT_DIR".

# Build output directory
OUTPUT_DIR = build
# Path to executable "wskdeploy"
WSKDEPLOY = ../wskdeploy

TARGETS := $(wildcard src/*/.)
CLEAN_TARGETS := $(addsuffix .clean,$(TARGETS)) 

.PHONY: all $(TARGETS) clean $(CLEAN_TARGETS) deploy

all: $(TARGETS)

build:
	mkdir -p $(OUTPUT_DIR)

$(TARGETS): src/%/.: | build
	@echo Runtime target: $*
	$(MAKE) -C $@
	@echo Copy action environments of target to build output directory
	@mkdir -p "$(OUTPUT_DIR)/$*"
	@cp -u $@/*.zip "$(OUTPUT_DIR)/$*/"

clean: $(CLEAN_TARGETS)
	rm -rf $(OUTPUT_DIR)/*

$(CLEAN_TARGETS): %.clean:
	@echo Clean target: $*
	$(MAKE) -C $* clean

deploy: manifest.yml
	$(WSKDEPLOY) -P swift_parameters.json
