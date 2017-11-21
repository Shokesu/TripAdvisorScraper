#!/bin/sh

git pull origin master
cd TripAdvisorScraper
cp settings.prod.py settings.py
cd ..
cd web
cp run.prod.py run.py
