import click
from taskcrafter.job_loader import load_jobs, job_get, validate
from taskcrafter.plugin_loader import plugin_list, plugin_execute, init_plugins

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
              help='Name of the jobs file (default: {JOBS_FILE}).')
def list(file=JOBS_FILE):
    """List all jobs from YAML file."""
    click.echo(f"Listing all jobs from {file}...")
    validate(file)

    data = load_jobs(file)

    for job in data.get("jobs", []):
        click.echo(f"  {job['id']} - {job.get('name', 'No name')}")


@cli.command()
@click.option('--file', default=JOBS_FILE, help='Name of the file.')
@click.argument('job', type=str)
def run(job, file=JOBS_FILE):
    """Run a job from YAML file."""

    validate(file)

    init_plugins()
    data = load_jobs(file)
    job = job_get(job, data)

    click.echo(f"Running job: {job['id']} with plugin {job['plugin']}...")

    plugin_execute(job["plugin"], job.get("params", {}))


@cli.command()
def plugins():
    """List all available plugins."""
    click.echo("Listing all available plugins...")
    init_plugins()
    plugins = plugin_list()

    if not plugins:
        click.echo("No plugins found.")
        return
    for name, description in plugins:
        click.echo(f"  {name} - {description}")


if __name__ == "__main__":
    cli()
