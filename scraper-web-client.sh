#!/bin/sh

export PYTHONPATH=$PWD
python3 web/__init__.py "$*"