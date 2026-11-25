SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHON ?= python3

.PHONY: all lint-qml check-settings test test-portable test-hardware provenance build-mandara verify-cachyos install clean package

all: provenance lint-qml check-settings test-portable

provenance:
	PYTHONPATH="$(ROOT_DIR)/src" $(PYTHON) "$(ROOT_DIR)/bin/scy-shell" provenance

check-settings:
	$(PYTHON) "$(ROOT_DIR)/scripts/check-studio-settings.py"

lint-qml:
	"$(ROOT_DIR)/scripts/lint-qml.sh"

test-portable: lint-qml
	PYTHONPATH="$(ROOT_DIR)/src" $(PYTHON) -m unittest discover -s "$(ROOT_DIR)/tests" -p "test_phase*.py" -v

test-hardware:
	PYTHONPATH="$(ROOT_DIR)/src" $(PYTHON) -m unittest discover -s "$(ROOT_DIR)/tests/hardware" -p "test_*.py" -v

test: lint-qml
	"$(ROOT_DIR)/scripts/run-tests.sh"

build-mandara:
	"$(ROOT_DIR)/scripts/build-clean.sh"

verify-cachyos:
	"$(ROOT_DIR)/scripts/verify-cachyos-live.sh"

install:
	"$(ROOT_DIR)/install.sh" --profile full --with-hypr

package:
	"$(ROOT_DIR)/scripts/package-release.sh"

clean:
	find "$(ROOT_DIR)" -type d -name "__pycache__" -prune -exec rm -rf {} +
	find "$(ROOT_DIR)" -type f -name "*.pyc" -delete
