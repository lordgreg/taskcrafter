import time
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import (
    EVENT_ALL,
    JobExecutionEvent,
    JobSubmissionEvent,
    JobEvent,
)
from taskcrafter.logger import app_logger
from taskcrafter.job_loader import JobManager
from taskcrafter.hook_loader import HookManager
from taskcrafter.models.hook import HookType


class SchedulerManager:
    def __init__(self, job_manager: JobManager, hook_manager: HookManager):
        self.stores = {
            "default": MemoryJobStore(),
            "hooks": MemoryJobStore(),
        }
        self.scheduler = BackgroundScheduler(jobstores=self.stores)
        self.job_manager = job_manager
        self.hook_manager = hook_manager
        self.executed_hooks = []
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

        # check and execute BEFORE_ALL hook
        self.schedule_hook_jobs(HookType.BEFORE_ALL)

        # Add a shutdown hook to stop the scheduler when the application exits
        try:
            while not self._event.is_set():
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.stop_scheduler()
            app_logger.info("Scheduler stopped.")

    def event_listener_job(self, event):
        if isinstance(event, JobEvent):
            job_id = self.get_job_id_from_schedule_id(event.job_id)

        if isinstance(event, JobSubmissionEvent):
            self.schedule_hook_jobs(HookType.BEFORE_JOB, event)
            self.job_manager.job_get_by_id(job_id).result.start()
        elif isinstance(event, JobExecutionEvent):
            if event.exception:
                self.schedule_hook_jobs(HookType.ON_ERROR, event)
                app_logger.error(
                    f"scheduler: {event.job_id} failed with exception: {event.exception}"
                )

            self.schedule_hook_jobs(HookType.AFTER_JOB, event)

            self.job_manager.job_get_by_id(job_id).result.stop()
            if self.job_manager.get_in_progress() == 0:
                hook_executed = self.schedule_hook_jobs(HookType.AFTER_ALL, event)

                # stop only when hook was executed or is None
                if hook_executed is None:
                    app_logger.info("No more jobs in progress.")
                    self._event.set()

    def get_job_id_from_schedule_id(self, schedule_id):
        # if schedule_id is "Hook(<hookType>)__<jobId>"
        if schedule_id.startswith("Hook("):
            return schedule_id.split("__")[1]

        return schedule_id

    def schedule_hook_jobs(self, hookType: HookType, event=None):
        try:
            hook = self.hook_manager.hook_get_by_type(hookType) or None
            if hook is not None and hook in self.executed_hooks:
                app_logger.info(f"Hook already executed: {hook.type}")
                return None

            self.executed_hooks.append(hook)

        except ValueError:
            return None

        try:
            hook = self.hook_manager.hook_get_by_type(hookType)
            for job in hook.jobs:
                schedule_job_id = f"Hook({hook.type})__{job.id}"
                app_logger.info(f"Executing hook {hook.type} - {job.id}")
                self.schedule_job(
                    job,
                    force=True,
                    is_hook=True,
                    schedule_job_id=schedule_job_id,
                )
            return hook
        except ValueError:
            # it just means we dont have a hook defined in yaml file
            pass

    def schedule_job(self, job, schedule_job_id=None, is_hook=False, force=False):
        cron_schedule = job.schedule
        job_id = job.id

        if schedule_job_id:
            job_id = schedule_job_id

        if job.enabled is False and not force:
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
            kwargs={"force": force},
            id=job_id,
            jobstore="hooks" if is_hook else "default",
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
