from rich.console import Console
from rich.tree import Tree


def rich_preview(jobs):
    console = Console()
    tree = Tree("TaskCrafter Jobs")

    for job in jobs:
        if job.enabled:
            node = tree.add(f"[bold green]{job.id}[/bold green]: {job.name}")
        else:
            node = tree.add(
                f"[yellow]{job.id}[/yellow]: {job.name} [dim](disabled)[/dim]"
            )
        for dep in job.depends_on or []:
            node.add(f"[dim]depends_on: {dep}[/dim]")
        for succ in job.on_success or []:
            node.add(f"[green]on_success: {succ}[/green]")
        for fail in job.on_failure or []:
            node.add(f"[red]on_failure: {fail}[/red]")
        for finish in job.on_finish or []:
            node.add(f"[blue]on_finish: {finish}[/blue]")
        if job.timeout:
            node.add(f"[yellow]timeout: {job.timeout} seconds[/yellow]")
        if job.max_retries.count > 0:
            node.add(
                f"[orange]max_retries: {job.max_retries.count} every {job.max_retries.interval} seconds[/orange]"
            )

    console.print(tree)
