#! /bin/bash
cd /Users/nellekesmits/Documents/projects/service.sensor-data/frontend/

source ../venv/bin/activate
export FLASK_APP=sensor_webserver_graph.py
export FLASK_ENV=development
flask run --host=0.0.0.0
