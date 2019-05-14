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

LOGGER = logging.getLogger(__name__)

class WinService(win32serviceutil.ServiceFramework):
    _svc_name_ = "mytest-service"
    _svc_display_name_ = "mytest service"
 
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
        LOGGER.info("... STOPPING SCHEDULE SERVICE ... \n")
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
        print("HELLO {}".format(index))

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        LOGGER.info("... STARTING SCHEDULE PROCESS ...\n")

        index = 0
        while not self.stop_requested:
            if index > 5: break
            self.test1(index)
            index += 1
            time.sleep(1)

if __name__ == '__main__':
    WinService.parse_command_line()