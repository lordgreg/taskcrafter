import yaml
import click
import util

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

    f = util.load_file(file)

    data = yaml.safe_load(f)
    if data is None:
        click.echo("No data found in the file.")
        exit(1)

    for job in data.get("jobs", []):
        click.echo(f"  {job['id']} - {job.get('name', 'No name')}")


@cli.command()
@click.option('--file', default=JOBS_FILE, help='Name of the file.')
@click.argument('job', type=str)
def run(job, file=JOBS_FILE):
    """Run a job from YAML file."""
    f = util.load_file(file)

    # TODO: validate the yaml file
    # util.yaml_validate("jobs", f)

    data = yaml.safe_load(f)

    # check if job exists
    job = next((j for j in data.get("jobs", []) if j["id"] == job), None)

    if job is None:
        click.echo(f"Job {job} does not exist.")
        exit(1)

    click.echo(f"Running job: {job['id']} with plugin {job['plugin']}...")
    util.plugin_load(job["plugin"], job.get("params", {}))


@cli.command()
def plugins():
    """List all available plugins."""
    click.echo("Listing all available plugins...")
    plugins = util.plugin_list()

    if not plugins:
        click.echo("No plugins found.")
        return
    for plugin in plugins:
        click.echo(f"  {plugin['name']} - {plugin['description']}")


if __name__ == "__main__":
    cli()
