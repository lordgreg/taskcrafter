import click
from taskcrafter.job_loader import JobManager
from taskcrafter.plugin_loader import plugin_list, init_plugins
from taskcrafter.scheduler import SchedulerManager
from taskcrafter.logger import app_logger
from taskcrafter.preview import rich_preview
from taskcrafter.models.app_config import AppConfig

JOBS_FILE = "jobs/jobs.yaml"

app_config = AppConfig()


@click.group()
@click.option(
    "--file",
    type=click.Path(exists=True),
    default=JOBS_FILE,
    help="Name of the jobs file (yaml).",
)
def cli(file=JOBS_FILE):
    """CLI for TaskCrafter."""

    app_config.jobs_file = file


@cli.command()
def help():
    """Display help information."""
    click.echo("This is the help command. Use --help for more information.")


@cli.command()
def list():
    """List all jobs from YAML file."""
    app_logger.info(f"Listing all jobs from {app_config.jobs_file}...")

    jobManager = JobManager(app_config.jobs_file)
    jobManager.validate()

    for job in jobManager.jobs:
        app_logger.info(f"  {job.id} - {job.name}")


@cli.command()
@click.option("--job", help="Name of the job.")
def run(job):
    """Run a job from YAML file."""

    jobManager = JobManager(app_config.jobs_file)
    jobManager.validate()

    init_plugins()

    if job:
        job = jobManager.job_get_by_id(job, jobManager.jobs)
        jobManager.jobs = [job]

    schedulerManager = SchedulerManager(jobManager)

    for job in jobManager.jobs:
        schedulerManager.schedule_job(job)

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


@cli.command()
def preview():
    """Preview the job dependency graph."""
    jobs = JobManager(app_config.jobs_file).jobs
    rich_preview(jobs)


if __name__ == "__main__":
    cli()
