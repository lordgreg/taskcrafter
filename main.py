import click
from taskcrafter.job_loader import JobManager
from taskcrafter.plugin_loader import plugin_list, init_plugins
from taskcrafter.scheduler import SchedulerManager
from taskcrafter.logger import app_logger

JOBS_FILE = "jobs/jobs.yaml"


@click.group()
def cli():
    """CLI for TaskCrafter."""
    pass


@cli.command()
def help():
    """Display help information."""
    click.echo("This is the help command. Use --help for more information.")


@cli.command()
@click.option('--file', default=JOBS_FILE,
              help=f'Name of the jobs file (default: {JOBS_FILE}).')
def list(file=JOBS_FILE):
    """List all jobs from YAML file."""
    app_logger.info(f"Listing all jobs from {file}...")

    jobManager = JobManager(file)
    jobManager.validate()

    for job in jobManager.jobs:
        app_logger.info(f"  {job.id} - {job.name}")


@cli.command()
@click.option('--job', help='Name of the job.')
@click.option('--file', default=JOBS_FILE, help='Name of the file.')
def run(job, file=JOBS_FILE):
    """Run a job from YAML file."""

    jobManager = JobManager(file)
    jobManager.validate()

    init_plugins()

    if job:
        job = jobManager.job_get_by_id(job, jobs)
        jobManager.jobs = [job]

    # filter jobs, if .enabled=True
    jobs = [j for j in jobManager.jobs if j.enabled is True]

    has_scheduled_jobs = len([j for j in jobs if j.schedule]) > 0

    if has_scheduled_jobs:
        schedulerManager = SchedulerManager(jobManager)


    for job in jobs:
        if job.schedule:
            schedulerManager.schedule_job(job)
        else:
            jobManager.run_job(job)

    if has_scheduled_jobs:
        schedulerManager.start_scheduler()


@cli.command()
def plugins():
    """List all available plugins."""
    app_logger.info("Listing all available plugins...")
    init_plugins()
    plugins = plugin_list()

    if not plugins:
        click.echo("No plugins found.")
        app_logger.warning("No plugins found.")
        return
    for name, description in plugins:
        app_logger.info(f"Plugin {name} - {description}")


if __name__ == "__main__":
    cli()
