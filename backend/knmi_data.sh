#! /bin/bash
cd /home/pi/Documents/service.sensor-data/backend/

source ../venv/bin/activate
python src/knmi_data.py R,1
