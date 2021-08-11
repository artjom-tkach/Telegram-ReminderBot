from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


# Модуль scheduler

class Scheduler:
    jobstores = {
        'default': MemoryJobStore()
    }
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(10)
    }
    job_defaults = {
        'coalesce': True,  # The accumulated task only runs once
        'max_instances': 1000,  # Support 1000 concurrent instances
        'misfire_grace_time': 600  # 600 seconds task timeout fault tolerance
    }

    scheduler = None
    error = 0

    def __init__(self):
        try:
            self.scheduler = BackgroundScheduler(jobstores=self.jobstores, executors=self.executors,
                                                 job_defaults=self.job_defaults)
            self.start()
        except Exception:
            self.error = 1
            print("Scheduler is not working!")

    def start(self):
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            self.error = 1
            print("Scheduler did not started!")
