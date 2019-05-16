import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
import schedule 
import croniter
import datetime

from web_scrapper.utils.utils import *
from data_collector.runner.runner import Runner as DataCollector

class DataCollectorService(win32serviceutil.ServiceFramework):

    setup_logging('windows_service_logging.yaml')

    LOGGER = logging.getLogger(__name__)
    SERVER_CONFIG = get_server_config()
    WINDOWS_SERVICE_CONFIG = get_windows_service_config(LOGGER)

    _svc_name_ = WINDOWS_SERVICE_CONFIG['svc_name']
    _svc_display_name_ = WINDOWS_SERVICE_CONFIG['svc_display_name']
    
    @classmethod
    def parse_command_line(cls):
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        socket.setdefaulttimeout(60)

        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
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

    def main(self):
        this_cron = None

        while not self.stop_requested:
            this_cron = self.scheduled_work(this_cron)
            time.sleep(1)

    def scheduled_work(self, prev_cron):
        period = self.WINDOWS_SERVICE_CONFIG['time']

        now = datetime.datetime.now().replace(microsecond=0)
        cron = croniter.croniter(period, now)
        next_cron = cron.get_next(datetime.datetime)

        is_cron_updated = False if not prev_cron else prev_cron != next_cron

        if is_cron_updated:
            self.LOGGER.info("HIT @ time: {}".format(now))
            data_collector = DataCollector(self.WINDOWS_SERVICE_CONFIG['ticker'], num_threads=4)
            data_collector.run()
        else:
            self.LOGGER.info("@ time: {}, prev_cron: {}, next_cron: {}".format(now, prev_cron, next_cron))

        return next_cron

if __name__ == '__main__':
    DataCollectorService.parse_command_line()