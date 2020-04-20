#!/bin/bash

#export FLASK_APP=redistest.py
export FLASK_APP=receive.py
#export FLASK_APP=ws_v31.py
#export FLASK_APP=ws_v32_redis.py
export FLASK_ENV=development

flask run --port=2000 --host=0.0.0.0
