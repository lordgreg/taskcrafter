from rich.tree import Tree
from rich.table import Table
from rich.console import Console
from rich.text import Text
from taskcrafter.models.job import Job, JobStatus
from taskcrafter.models.hook import Hook
from taskcrafter.models.plugin import PluginEntry

console = Console()


def rich_preview(jobs: list[Job], hooks: list[Hook] = []):
    tree = Tree("[bold green]Jobs")

    for job in jobs:
        label = f"[dim][s]{job.id}" if not job.enabled else f"[bold]{job.id}"
        job_branch = tree.add(f"{label} — {job.name}")

        if job.plugin:
            job_branch.add(f"Plugin: [cyan]{job.plugin}[/]")
        elif job.container:
            container_info = f"[magenta]{job.container.image}[/]"
            job_branch.add(f"Container: {container_info}")

        if job.schedule:
            job_branch.add(f"Schedule: [blue]{job.schedule}[/]")

        if job.timeout:
            job_branch.add(f"Timeout: {job.timeout}s")

        if job.retries and (job.retries.count > 0 or job.retries.interval > 0):
            job_branch.add(
                f"Retries: [bold]{job.retries.count}[/] every "
                f"[bold]{job.retries.interval}s[/]"
            )

        if job.depends_on:
            job_branch.add("Depends on: " + ", ".join(job.depends_on))

        if job.on_success:
            job_branch.add("On Success: " + ", ".join(job.on_success))
        if job.on_failure:
            job_branch.add("On Failure: " + ", ".join(job.on_failure))
        if job.on_finish:
            job_branch.add("On Finish: " + ", ".join(job.on_finish))

    console.print(tree)

    if len(hooks) > 0:
        tree = Tree("\n[bold green]Hooks")

        for hook in hooks:
            hook_branch = tree.add(f"[bold]{hook.type.value}")

            for job in hook.jobs:
                hook_branch.add(f"{job.id}")

        console.print(tree)


def result_table(jobs: list[Job]):
    console = Console()
    table = Table(title="Job Execution Summary")

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Status", style="bold")
    table.add_column("Retries", style="bold")
    table.add_column("Stack", style="bold")
    table.add_column("Duration", style="bold")

    # sort by result.start_time
    jobs = sorted(jobs, key=lambda x: x.result.start_time)

    for job in jobs:
        match job.result.status:
            case JobStatus.ERROR:
                status = Text(job.result.get_status().value, "red")
            case JobStatus.SUCCESS:
                status = Text(job.result.get_status().value, "green")
            case _:
                continue

        table.add_row(
            str(job.id),
            job.name,
            status,
            str(job.result.retries),
            " > ".join(job.result.execution_stack),
            f"{job.result.get_elapsed_time():.3f}s",
        )

    console.print(table)


def plugin_list_preview(plugins: list[PluginEntry]):
    console = Console()

    table = Table(title="Plugin list")

    table.add_column("Id", style="cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Description")

    for plugin in plugins:
        table.add_row(plugin.id, plugin.name, plugin.description)

    console.print(table)


def plugin_info_preview(plugin: PluginEntry):
    console = Console()

    console.print(f"[bold cyan]Plugin Info - {plugin.name}[/]")
    console.print(f"[bold]Id:[/] {plugin.id}")
    console.print(f"[bold]Name:[/] {plugin.name}")
    console.print(f"[bold]Description:[/] {plugin.description}")
    console.print(f"[bold]Class:[/] {plugin.__class__.__name__}")
    console.print(f"[bold]Module:[/] {plugin.instance.__module__}")

    if not plugin.docgen:
        docgen = "[italic]No documentation available.[/]"
    else:
        docgen = plugin.docgen

    console.print(f"\n{docgen}")
