#!/bin/bash

if [ "$1" = "api" ]
then
    echo "Start API server ..."
    gunicorn --workers=4 -b 0.0.0.0:5000 trade-advisor-api:app
elif [ "$1" = "ws" ]
then
    echo "Start Websocket server ..."
    python ./trade-advisor-ws.py
else
    echo "Please specify the server type Currently supported server type [api, ws]"
fi