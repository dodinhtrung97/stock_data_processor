@echo off

set PWD=%~dp0
echo %PWD%
set DEFAULT_SERVICE_LOG_DIRECTORY_NAME=logs
set SERVICE_NAME=Scheduled Data Collector

set SERVICE_LOG_PATH=%PWD%\%DEFAULT_SERVICE_LOG_DIRECTORY_NAME%
set SERVICE_RUNNER_PATH=%PWD%\src\data_collector_service.py
set SERVICE_REQUIREMENT_PATH=%PWD%\requirements.txt

echo INFO: Using default .\logs directory for service logging
if not exist %SERVICE_LOG_PATH% call md %SERVICE_LOG_PATH%

echo INFO: Installing pip dependencies
call pip install -r %SERVICE_REQUIREMENT_PATH%

echo INFO: Starting %SERVICE_NAME% service with logs at %SERVICE_LOG_PATH%
call python %SERVICE_RUNNER_PATH% install
call python src\data_collector_service.py start --log_dir=%SERVICE_LOG_PATH%

echo INFO: Service %SERVICE_NAME% started