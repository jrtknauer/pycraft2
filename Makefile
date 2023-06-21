###############################################################################
# pycraft2 Makefile
#
# While no style for the makefile is strictly enforced, I've drawn most of
# the organization from https://clarkgrubb.com/makefile-style-guide and
# https://www.gnu.org/software/make/manual/make.html#Makefile-Conventions
# Review both style guide prior to making changes.
#
###############################################################################

###############################################################################
# Common variables
###############################################################################

SHELL = /bin/sh

## Virtual environment
PROJECT := pycraft2
PYTHON_VERSION ?= 3.10.12
VENV := .$(PROJECT)-$(PYTHON_VERSION)
VENV_DIR := $(shell pyenv root)/versions/$(VENV)

## Directories
REQUIREMENTS_DIR := requirements
PYTHON_ARTIFACTS := *.egg-info .tox/ .ruff_cache/
BUILD_ARTIFACTS := dist/ build/

## Executables
PYTHON ?= $(VENV_DIR)/bin/python
PIP ?= $(VENV_DIR)/bin/pip
PIP_COMPILE ?= $(VENV_DIR)/bin/pip-compile
PIP_SYNC ?= $(VENV_DIR)/bin/pip-sync
BLACK ?= $(VENV_DIR)/bin/black
ISORT ?= $(VENV_DIR)/bin/isort
PYRIGHT ?= $(VENV_DIR)/bin/pyright
RUFF ?= $(VENV_DIR)/bin/ruff
TOX ?= $(VENV_DIR)/bin/tox
PYENV ?= pyenv

## Flag defaults
PIP_COMPILE_FLAGS ?= --allow-unsafe --resolver=backtracking

## Terminal output visuals
STDOUT_GREEN := $(shell tput -Txterm setaf 2)
STDOUT_INFO := $(STDOUT_GREEN)-->
STDOUT_OFF := $(shell tput sgr0)

###############################################################################
# Default targets
###############################################################################

.DEFAULT_GOAL := help

.PHONY: all
all: distclean clean build install

.PHONY: default
default: help

.PHONY: help
help:

###############################################################################
# Build targets
###############################################################################

.PHONY: build
build: venv depends

.PHONY: venv
venv:
	@echo "$(STDOUT_INFO) Creating virtual environment...$(STDOUT_OFF)"
	$(PYENV) virtualenv $(PYTHON_VERSION) $(VENV)

.PHONY: depends
depends:
	@echo "$(STDOUT_INFO) Upgrading pip...$(STDOUT_OFF)"
	$(PIP) install --upgrade pip

	@echo "$(STDOUT_INFO) Installing pip-tools...$(STDOUT_OFF)"
	$(PIP) install --upgrade pip-tools

	@echo "$(STDOUT_INFO) Compiling pins from requirements...$(STDOUT_OFF)"
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) $(REQUIREMENTS_DIR)/base.in
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) $(REQUIREMENTS_DIR)/test.in
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) $(REQUIREMENTS_DIR)/dev.in

	@echo "$(STDOUT_INFO) Installing dependencies...$(STDOUT_OFF)"
	$(PIP_SYNC) $(REQUIREMENTS_DIR)/*.txt --pip-args "--upgrade --no-cache-dir"

###############################################################################
# Test targets
###############################################################################

# Runs all tox environments, including any linter checks. Use format to apply
# linter changes in the virtual environment.
.PHONY: check
check:
	$(TOX)

###############################################################################
# Lint targets
###############################################################################

# Run formatters and check results with linters in virtual environment
.PHONY: format
format:
	$(ISORT) .
	$(BLACK) .
	$(RUFF) check .
	$(PYRIGHT) --venvpath $(VENV_DIR)

###############################################################################
# Documentation targets
###############################################################################

.PHONY: info
info:

###############################################################################
# Install targets
###############################################################################

.PHONY: install
install:
	$(PIP) install --editable .

###############################################################################
# Clean targets
###############################################################################

.PHONY: clean
clean:
	@echo "$(STDOUT_INFO) Deleting build and test artifacts...$(STDOUT_OFF)"
	rm -rf $(PYTHON_ARTIFACTS) $(BUILD_ARTIFACTS)

.PHONY: distclean
distclean: clean
	@echo "$(STDOUT_INFO) Deleting virtual environment...$(STDOUT_OFF)"
	pyenv virtualenv-delete --force $(VENV)
