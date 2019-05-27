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
import os

from web_scrapper.utils.utils import *
from data_collector.runner.runner import Runner as DataCollector

class DataCollectorService(win32serviceutil.ServiceFramework):
    LOGGER = logging.getLogger(__name__)
    WINDOWS_SERVICE_CONFIG = get_server_config()

    _svc_name_ = WINDOWS_SERVICE_CONFIG['SERVICE']['SVC_NAME']
    _svc_display_name_ = WINDOWS_SERVICE_CONFIG['SERVICE']['SVC_DISPLAY_NAME']
    
    @classmethod
    def parse_command_line(cls):
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        socket.setdefaulttimeout(60)

        self.log_dir = None
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False
        self.cron_period = self.WINDOWS_SERVICE_CONFIG['SERVICE']['CRON_PERIOD'].strip()

        self.process_cmd_args(args=args)
        setup_service_logging(log_dir_path=self.log_dir)

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

    def scheduled_work(self, prev_cron):
        """
        Collect data with cron time defined in ~/conf/windows_service_config.json
        """
        current_time = datetime.datetime.now().replace(microsecond=0)
        current_cron = croniter.croniter(self.cron_period, current_time)
        next_cron = current_cron.get_next(datetime.datetime)

        is_cron_updated = False if not prev_cron else prev_cron != next_cron

        if is_cron_updated:
            self.LOGGER.info("Collecting data at time: {}".format(current_time))
            data_collector = DataCollector(num_threads=4)
            data_collector.run()
        else:
            self.LOGGER.debug("@ time: {}, next_cron: {}".format(current_time, next_cron))

        return next_cron

    def main(self):
        self.LOGGER.info("Started scheduled job with cron: {}".format(self.WINDOWS_SERVICE_CONFIG['SERVICE']['CRON_PERIOD'].strip()))
        current_cron = None

        while not self.stop_requested:
            current_cron = self.scheduled_work(current_cron)
            time.sleep(1)

    def process_cmd_args(self, args):
        """
        Process command line argument, retrives log directory path
        """
        ARG_NAME = '--log_dir'

        if len(args) == 2:
            args = args[1:][0]
            arg, value = args.split('=', 1)

            if not os.path.isdir(value):
                raise OSError("Input path does not exists, failed to create log files for service")

            self.log_dir = value if arg == ARG_NAME else None

            if not self.log_dir: os.exit(1)

if __name__ == '__main__':
    DataCollectorService.parse_command_line()