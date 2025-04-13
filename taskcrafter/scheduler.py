import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from taskcrafter.logger import app_logger
from taskcrafter.job_loader import run_job

scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Start the APScheduler.
    """
    if scheduler.running:
        app_logger.warning("Scheduler is already running.")
        return

    scheduler.add_listener(
            event_listener_job, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()

    # Add a shutdown hook to stop the scheduler when the application exits
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        app_logger.info("Scheduler stopped.")


def execute_scheduled_job(job):
    """
    Execute a scheduled job by its ID.
    """
    app_logger.info(f"Executing scheduled job: {job.id}")



def event_listener_job(event):
    if event.exception:
        app_logger.error(
                f"Job {event.job_id} failed with exception: {event.exception}")


def schedule_job(job):
    cron_schedule = job.schedule
    job_id = job.id

    if not cron_schedule:
        app_logger.warning(
                f"Job {job_id} does not have a schedule. Skipping...")
        return

    CronTrigger.from_crontab
    scheduler.add_job(
        execute_scheduled_job,
        trigger=CronTrigger.from_crontab(cron_schedule),
        args=[job],
        id=job_id,
    )

    app_logger.info(
            f"Scheduled job {job_id} with cron schedule: {cron_schedule}")
