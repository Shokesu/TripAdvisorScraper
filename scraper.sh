#!/bin/sh

export PYTHONPATH=$PWD
python3 TripAdvisorScraper/crawl.py "$*"