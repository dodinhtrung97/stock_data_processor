@echo off

set PWD=%cd%
set DEFAULT_SERVICE_LOG_DIRECTORY_NAME=logs
set SERVICE_NAME=Scheduled Data Collector

set SERVICE_LOG_PATH=%PWD%\%DEFAULT_SERVICE_LOG_DIRECTORY_NAME%

echo INFO: Installing pip dependencies
start cmd /k pip install -r requirements.txt

echo INFO: Starting %SERVICE_NAME% service with logs at %SERVICE_LOG_PATH%
start cmd /k python src\data_collector_service.py debug --log_dir=%SERVICE_LOG_PATH%