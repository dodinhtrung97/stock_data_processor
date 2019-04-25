class Job:
    
    def __init__(self, name, exec, *args):
        self.name = name
        self.exec = exec
        self.args = args

    def get_job_info(self):
        return 'Job info: [name: {0}, exec: {1}, args: {2}]'.format(self.name, self.exec, self.args)