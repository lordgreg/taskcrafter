import click
from taskcrafter.logger import app_logger
from taskcrafter.util.file import get_file_content
from taskcrafter.job_loader import JobManager
from taskcrafter.hook_loader import HookManager
from taskcrafter.plugin_loader import plugin_list, init_plugins, plugin_lookup
from taskcrafter.scheduler import SchedulerManager
from taskcrafter.preview import (
    rich_preview,
    result_table,
    plugin_info_preview,
    plugin_list_preview,
)
from taskcrafter.config import app_config
from taskcrafter.util.validator import validate_hooks, validate_jobs, validate_schema
from taskcrafter.util.yaml import get_yaml_from_string

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


def validate_and_initialize():
    """Reads file, validates schema, initializes plugins, and sets up managers."""

    try:
        file_content = get_file_content(app_config.jobs_file)
        yaml = get_yaml_from_string(file_content)
        validate_schema(yaml)
        init_plugins(yaml)

        jobManager = JobManager(file_content)
        hookManager = HookManager(file_content, job_manager=jobManager)

        validate_jobs(jobManager.jobs)
        validate_hooks(hookManager.hooks)
    except Exception as e:
        app_logger.error(f"{e.__class__.__name__}: {e}")
        return None, None

    return jobManager, hookManager


def run_helper(job_id: str):
    """
    Core logic for running jobs. Can be called programmatically.
    """
    global schedulerManager

    jobManager, hookManager = validate_and_initialize()
    if jobManager is None or hookManager is None:
        return

    if job_id:
        try:
            job = jobManager.job_get_by_id(job_id)
        except ValueError:
            app_logger.error(f"Job {job_id} does not exist.")

        jobManager.jobs = [job]

    schedulerManager = SchedulerManager(
        job_manager=jobManager, hook_manager=hookManager
    )

    for job in jobManager.jobs:
        schedulerManager.schedule_job(job)

    schedulerManager.start_scheduler()

    result_table(jobManager.executed_jobs)


@click.group()
def jobs():
    """Manage jobs."""


@jobs.command()
@click.option("--job", "job_id", help="Name of the job.")
def run(job_id: str):
    """
    Runs all jobs from YAML file.
    If a --job parameter is provided, it runs only that job.
    Restarts if app_config.jobs_file changes.
    """

    run_helper(job_id)


@jobs.command()
def validate():
    """Validate jobs from YAML file."""
    jobManager, hookManager = validate_and_initialize()
    if jobManager is None or hookManager is None:
        return


@jobs.command()
def list():
    """List all jobs from YAML file."""
    jobManager, hookManager = validate_and_initialize()
    if jobManager is None or hookManager is None:
        return

    rich_preview(jobManager.jobs, hookManager.hooks)


@click.group()
def plugins():
    """Manage TaskCrafter plugins."""
    validate_and_initialize()


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


cli.add_command(jobs)
cli.add_command(plugins)


if __name__ == "__main__":
    cli()
