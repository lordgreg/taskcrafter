import click
from taskcrafter.job_loader import load_jobs, job_get, validate, run_job
from taskcrafter.plugin_loader import plugin_list, init_plugins
from taskcrafter.scheduler import schedule_job, start_scheduler
from taskcrafter.logger import app_logger

JOBS_FILE = "jobs/my_jobs.yaml"


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
    validate(file)

    jobs = load_jobs(file)

    for job in jobs:
        app_logger.info(f"  {job.id} - {job.name}")


@cli.command()
@click.option('--job', help='Name of the job.')
@click.option('--file', default=JOBS_FILE, help='Name of the file.')
def run(job, file=JOBS_FILE):
    """Run a job from YAML file."""

    validate(file)

    init_plugins()
    jobs = load_jobs(file)
    has_scheduled_jobs = False

    if job:
        job = job_get(job, jobs)
        jobs = [job]

    # filter jobs, if .enabled=True
    jobs = [j for j in jobs if j.enabled is True]

    for job in jobs:
        if job.schedule:
            has_scheduled_jobs = True
            schedule_job(job)
        else:
            app_logger.info(
                    f"Running job: {job.id} with plugin {job.plugin}...")
            run_job(job)

    if has_scheduled_jobs:
        start_scheduler()


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
