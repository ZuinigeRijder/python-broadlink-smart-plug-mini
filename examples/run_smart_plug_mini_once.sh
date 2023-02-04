#!/bin/bash
# ---------------------------------------------------------------
# A script to run smart_plug_mini once.
# if still running, kill the previous running script and start new one
# Add to your crontab to run once per hour a few minutes after whole hour
# 9 * * * * ~/smart_plug_mini/run_smart_plug_mini_once.sh >> ~/smart_plug_mini/run_smart_plug_mini_once.log 2>&1
# ---------------------------------------------------------------
script_name=$(basename -- "$0")
cd ~/smart_plug_mini

now=$(date)
if pidof -x "$script_name" -o $$ >/dev/null;then
   echo "$now: $script_name already running" >> run_smart_plug_mini_once.log 2>&1
   kill $(pidof $script_name) >> run_smart_plug_mini_once.log 2>&1
fi

/usr/bin/python -u ~/smart_plug_mini/smart_plug_mini.py >> run_smart_plug_mini_once.log 2>&1
