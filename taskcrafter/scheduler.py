import time
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import (
    EVENT_ALL,
    JobExecutionEvent,
    JobSubmissionEvent,
    JobEvent,
)
from taskcrafter.exceptions.hook import HookNotFound
from taskcrafter.exceptions.job import JobKillSignalError
from taskcrafter.logger import app_logger
from taskcrafter.job_loader import JobManager
from taskcrafter.hook_loader import HookManager
from taskcrafter.models.hook import Hook, HookType


class SchedulerManager:
    def __init__(self, job_manager: JobManager, hook_manager: HookManager):
        self.scheduler = BackgroundScheduler()
        self.job_manager = job_manager
        self.hook_manager = hook_manager
        self.executed_hooks: list[Hook] = []
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

        app_logger.debug("Scheduler started.")

        # check and execute BEFORE_ALL hook
        self.schedule_hook_jobs(HookType.BEFORE_ALL)

        # Add a shutdown hook to stop the scheduler when the application exits
        try:
            while not self._event.is_set():
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.stop_scheduler()
            app_logger.debug("Scheduler stopped.")

    def event_listener_job(self, event):
        if isinstance(event, JobEvent):
            job_id = self.get_job_id_from_schedule_id(event.job_id)

        if isinstance(event, JobSubmissionEvent):
            self.schedule_hook_jobs(HookType.BEFORE_JOB, event)
        elif isinstance(event, JobExecutionEvent):
            if event.exception:
                if isinstance(event.exception, JobKillSignalError):
                    app_logger.warning(
                        f"Job {job_id} is exit job, scheduler will be stopped."
                    )
                    self._event.set()
                    return

                self.schedule_hook_jobs(HookType.ON_ERROR, event)
                app_logger.error(
                    f"scheduler: {event.job_id} failed with exception: {event.exception}"
                )

            scheduler_job = self.scheduler.get_job(event.job_id)
            if scheduler_job is not None and isinstance(
                scheduler_job.trigger, CronTrigger
            ):
                app_logger.debug(
                    f"Job {job_id} is cron job and will be rescheduled. Scheduler wont be stopped."
                )
                return

            self.schedule_hook_jobs(HookType.AFTER_JOB, event)

            if self.job_manager.get_in_progress() == 0:
                hook_executed = self.schedule_hook_jobs(HookType.AFTER_ALL, event)

                # stop only when hook was executed or is None
                if hook_executed is None:
                    app_logger.info("No more jobs in progress.")
                    self._event.set()

    def get_job_id_from_schedule_id(self, schedule_id) -> str:
        # if schedule_id is "Hook(<hookType>)__<jobId>"
        if schedule_id.startswith("Hook("):
            return schedule_id.split("__")[1]

        return schedule_id

    def schedule_hook_jobs(self, hookType: HookType, event=None):
        # things can get messy here so:
        # the hook can get executed if:
        # - current event job isnt hook job
        # - hookType before_all or hookType after_all can get executed only once
        # - all other hookTypes can get executed several times
        try:
            hook = self.hook_manager.hook_get_by_type(hookType) or None

            # before_all and after_all dont have any parent.
            if (
                not hookType == HookType.BEFORE_ALL
                and not hookType == HookType.AFTER_ALL
            ):
                hook.parent_job = event.job_id

            if hook is None:
                app_logger.debug(f"Hook {hookType} does not exist.")
                return None
            elif hook.is_hook_job():
                app_logger.debug(
                    f"Job {event.job_id} is hook job. Hook {hookType} will not be executed."
                )
                return None
            elif hook in self.executed_hooks and hook.type in [
                HookType.BEFORE_ALL,
                HookType.AFTER_ALL,
            ]:
                app_logger.debug(f"Hook already executed: {hook.type}")
                return None

            self.executed_hooks.append(hook)

        except HookNotFound as e:
            app_logger.debug(e)
            return None

        try:
            for job in hook.jobs:
                # enable it
                job.enabled = True
                # add job to stack
                self.job_manager.add_job_to_stack(job)

                schedule_job_id = (
                    f"Hook({hookType.value};parent={event.job_id})__{job.id}"
                )

                self.schedule_job(
                    job,
                    force=True,
                    hook=hook,
                    schedule_job_id=schedule_job_id,
                )
            return hook
        except ValueError:
            pass

    def schedule_job(self, job, schedule_job_id=None, hook: Hook = None, force=False):
        cron_schedule = job.schedule
        job_id = job.id

        if schedule_job_id:
            job_id = schedule_job_id

        if job.enabled is False and not force:
            app_logger.debug(f"Job {job_id} is disabled and won't be executed.")
            return

        if not cron_schedule:
            trigger = DateTrigger(datetime.now())
        else:
            trigger = CronTrigger.from_crontab(cron_schedule)

        execution_stack = []
        if hook is not None:
            execution_stack = [f"Hook({hook.type.value};parent={hook.parent_job})"]

        self.scheduler.add_job(
            self.job_manager.run_job,
            trigger=trigger,
            args=[job],
            kwargs={
                "force": force,
                "execution_stack": execution_stack,
            },
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
