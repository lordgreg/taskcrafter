import pathlib
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
from taskcrafter.wizard import create_file_wizard

JOBS_FILE = "jobs/jobs.yaml"


schedulerManager: SchedulerManager = None


@click.group()
@click.option(
    "--file",
    "-f",
    type=click.Path(),
    default=JOBS_FILE,
    help="Name of the jobs file (yaml).",
)
def cli(file: str = JOBS_FILE):
    """CLI for TaskCrafter."""
    file_path = pathlib.Path(file)

    if not file_path.is_file():
        if not create_file_wizard(file_path):
            exit(1)

    app_config.jobs_file = file


@cli.command()
def help():
    """Display help information."""
    ctx = click.get_current_context()
    click.echo(cli.get_help(ctx))

    click.echo("\n🔍 Examples:\n")

    for command_name, command_obj in cli.commands.items():
        if hasattr(command_obj, "commands"):
            for subcommand_name in command_obj.commands:
                click.echo(f"  taskcrafter {command_name} {subcommand_name}")
        else:
            click.echo(f"  taskcrafter {command_name}")

    click.echo("\nℹ️  Use --help with any command to get more details.")
    click.echo("   e.g., taskcrafter jobs run --help\n")


def validate_and_initialize(show_report: bool = False):
    """Reads file, validates schema, initializes plugins, and sets up managers."""

    try:
        file_content = get_file_content(app_config.jobs_file)
        yaml = get_yaml_from_string(file_content)
        validate_schema(yaml)
        init_plugins(yaml)

        jobManager = JobManager(file_content)
        hookManager = HookManager(file_content, job_manager=jobManager)

        validate_jobs(jobManager.jobs, show_report=show_report)
        validate_hooks(hookManager.hooks, show_report=show_report)
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
@click.option("--job", "-j", "job_id", help="Name of the job.")
def run(job_id: str):
    """
    Runs all jobs from YAML file. If a --job parameter is provided, it runs only that job.

    Examples:

    \b
        taskcrafter jobs run
        taskcrafter jobs run --job job1
    """

    run_helper(job_id)


@jobs.command()
def validate():
    """Validate jobs from YAML file."""
    jobManager, hookManager = validate_and_initialize(show_report=True)
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
    """
    List all available plugins.

    Examples:

    \b
        taskcrafter plugins list
    """
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
    """
    Show detailed info about a specific plugin.

    Examples:

    \b
        taskcrafter plugins info echo
    """
    plugin = plugin_lookup(name)

    if not plugin:
        app_logger.error(f"Plugin {name} not found.")
        return

    plugin_info_preview(plugin)


cli.add_command(jobs)
cli.add_command(plugins)


if __name__ == "__main__":
    cli()
