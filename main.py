import click
from taskcrafter.logger import app_logger
from taskcrafter.job_loader import JobManager
from taskcrafter.plugin_loader import plugin_list, init_plugins, plugin_lookup
from taskcrafter.scheduler import SchedulerManager
from taskcrafter.preview import (
    rich_preview,
    result_table,
    plugin_info_preview,
    plugin_list_preview,
)
from taskcrafter.config import app_config

JOBS_FILE = "jobs/jobs.yaml"

schedulerManager: SchedulerManager = None


@click.group()
@click.option(
    "--file",
    type=click.Path(exists=True),
    default=JOBS_FILE,
    help="Name of the jobs file (yaml).",
)
def cli(file: str = JOBS_FILE):
    """CLI for TaskCrafter."""
    app_config.jobs_file = file


@cli.command()
def help():
    """Display help information."""
    click.echo("This is the help command. Use --help for more information.")


def run_helper(job_id: str):
    """
    Core logic for running jobs. Can be called programmatically.
    """
    global schedulerManager

    jobManager = JobManager(app_config.jobs_file)
    jobManager.validate()

    init_plugins()

    if job_id:
        try:
            job = jobManager.job_get_by_id(job_id)
        except ValueError:
            app_logger.error(f"Job {job_id} does not exist.")
        jobManager.jobs = [job]

    schedulerManager = SchedulerManager(jobManager)

    for job in jobManager.jobs:
        schedulerManager.schedule_job(job)

    schedulerManager.start_scheduler()

    result_table(jobManager.jobs)


@cli.command()
@click.option("--job", "job_id", help="Name of the job.")
def run(job_id: str):
    """
    Runs all jobs from YAML file.
    If a --job parameter is provided, it runs only that job.
    Restarts if app_config.jobs_file changes.
    """

    run_helper(job_id)


@cli.command()
def list():
    """List all jobs from YAML file."""
    jobs = JobManager(app_config.jobs_file).jobs
    rich_preview(jobs)


@click.group()
def plugins():
    """Manage TaskCrafter plugins."""
    init_plugins()


@plugins.command("list")
def plugins_list():
    """List all available plugins."""
    app_logger.info("Listing all available plugins...")
    plugins = plugin_list()

    if not plugins:
        click.echo("No plugins found.")
        app_logger.warning("No plugins found.")
        return

    plugin_list_preview(plugins)


@plugins.command("info")
@click.argument("name")
def plugin_info(name):
    """Show detailed info about a specific plugin."""
    plugin = plugin_lookup(name)

    if not plugin:
        app_logger.error(f"Plugin {name} not found.")
        return

    plugin_info_preview(plugin)


cli.add_command(plugins)


if __name__ == "__main__":
    cli()
