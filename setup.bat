@echo off

set PWD=%~dp0
set SERVER_REQUIREMENT_PATH=%PWD%requirements.txt

echo INFO: Installing pip dependencies
call pip install -r %SERVER_REQUIREMENT_PATH%