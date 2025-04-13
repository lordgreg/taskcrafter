import time
import sys
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_ALL,
    JobExecutionEvent,
    JobSubmissionEvent,
)
from taskcrafter.logger import app_logger
from taskcrafter.job_loader import JobManager


class SchedulerManager:
    def __init__(self, job_manager: JobManager):
        self.scheduler = BackgroundScheduler()
        self.job_manager = job_manager
        self._event = threading.Event()

    def start_scheduler(self):
        """
        Start the APScheduler.
        """
        if self.scheduler.running:
            app_logger.warning("Scheduler is already running.")
            return

        self.scheduler.add_listener(self.event_listener_job, EVENT_ALL)
        self.scheduler.start()

        app_logger.info("Scheduler started.")

        # Add a shutdown hook to stop the scheduler when the application exits
        try:
            while not self._event.is_set():
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.stop_scheduler()
            app_logger.info("Scheduler stopped.")

    def event_listener_job(self, event):
        if isinstance(event, Exception) and event.exception:
            app_logger.error(
                f"scheduler: {event.job_id} failed with exception: {event.exception}"
            )
        elif isinstance(event, JobSubmissionEvent):
            self.job_manager.job_get_by_id(event.job_id).result.start()
        elif isinstance(event, JobExecutionEvent):
            self.job_manager.job_get_by_id(event.job_id).result.stop()
            if self.job_manager.get_in_progress() == 0:
                app_logger.info(f"No more jobs.")
                self._event.set()

    def schedule_job(self, job):
        cron_schedule = job.schedule
        job_id = job.id

        if job.enabled is False:
            app_logger.warning(f"Job {job_id} is disabled and won't be executed.")
            return

        if not cron_schedule:
            trigger = DateTrigger(datetime.now())
        else:
            trigger = CronTrigger.from_crontab(cron_schedule)

        self.scheduler.add_job(
            self.job_manager.run_job,
            trigger=trigger,
            args=[job],
            id=job_id,
        )

        app_logger.info(
            f"Scheduled job {job_id} with scheduler {type(trigger).__name__}"
        )

    def stop_scheduler(self):
        """
        Stop the APScheduler.
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
            app_logger.info("Scheduler stopped.")
        else:
            app_logger.warning("Scheduler is not running.")
