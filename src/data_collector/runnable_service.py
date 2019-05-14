import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
import schedule 

import os
import yaml
import logging.config

class DataCollectorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "mytest-service"
    _svc_display_name_ = "mytest service"

    LOGGER = logging.getLogger(__name__)
 
    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.LOGGER.info("... STOPPING SCHEDULE SERVICE ... \n")
        self.stop_requested = True
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def test1(self, index):
        self.LOGGER.info("HELLO WORLD {}".format(index))

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        self.LOGGER.info("... STARTING SCHEDULE PROCESS ...\n")

        index = 0
        while not self.stop_requested:
            if index > 5: break
            self.test1(index)
            index += 1
            time.sleep(1)

if __name__ == '__main__':
    path = os.path.join('conf', 'logging.yaml')
    env_key = os.getenv('LOG_CFG', None)
    if env_key:
        path = env_key
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    DataCollectorService.parse_command_line()