import logging
import concurrent.futures
import os, time

class Processor():

    def __init__(self):
        pass
    def process(self, data, job, concurrency=os.cpu_count()):
        """ Actually do the execution. Currently using Pool class for parallel execution """
        pass

class MultiThreadingMeasurementProcessor(Processor):

    def __init__(self, logger=None):
        Processor.__init__(self)
        self.logger = logger or logging.getLogger(__name__)

    def process(self, files, job, concurrency=os.cpu_count()):
        self.logger.debug('Processing in multithreading job with info: %s', job.get_job_info())
        meas_type = job.args[0]
        pattern = job.args[1]
        days_forward = job.args[2]
        steps = job.args[3]
        
        rs = []
        self.logger.info('Running job with %s threads', concurrency)
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_results = { executor.submit(job.exec, file, meas_type, pattern, days_forward, steps): file for file in files }
            for future in concurrent.futures.as_completed(future_results):
                try:
                    result = future.result()
                except Exception as exc:
                    self.logger.error('Failed to process. Exception follows. %s', exc)
                else:
                    rs.append(result)
            return rs

class MultiProcessingMeasurementProcessor(Processor):

    def __init__(self, logger=None):
        Processor.__init__(self)
        self.logger = logger or logging.getLogger(__name__)

    def process(self, data, job, concurrency=os.cpu_count()):
        begin_time = time.time()

        self.logger.debug('Processing in multiprocessing job with info: %s', job.get_job_info())
        pattern_close_values = job.args[0]
        days_forward = job.args[1]
        steps = job.args[2]
        
        rs = []
        self.logger.info('Running job with %s processes', concurrency)
        with concurrent.futures.ProcessPoolExecutor(max_workers=concurrency) as executor:
            future_results = { executor.submit(job.exec, begin_time, ticker, dataframe, pattern_close_values, days_forward, steps): dataframe for ticker, dataframe in data.items()}
            for future in concurrent.futures.as_completed(future_results):
                try:
                    result = future.result()
                except Exception as exc:
                    self.logger.error('Failed to process. Exception follows. %s', exc)
                else:
                    rs.append(result)
            return rs
    