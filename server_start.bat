@echo off

set PWD=%~dp0

set DEFAULT_SERVER_LOG_DIRECTORY_NAME=logs
set DEFAULT_SERVER_SRC_DIRECTORY_NAME=src

set SERVER_LOG_PATH=%PWD%%DEFAULT_SERVER_LOG_DIRECTORY_NAME%
set SERVER_RUNNER_PATH=%PWD%%DEFAULT_SERVER_SRC_DIRECTORY_NAME%\app.py
set SERVER_REQUIREMENT_PATH=%PWD%requirements.txt

echo INFO: Using default .\logs directory for service logging
if not exist %SERVER_LOG_PATH% call md %SERVER_LOG_PATH%

echo INFO: Installing pip dependencies
call pip install -r %SERVER_REQUIREMENT_PATH%

start "Trade Advisor Backend Server" cmd /k python %SERVER_RUNNER_PATH% --logging=0