from rich.console import Console
from rich.tree import Tree


def rich_preview(jobs):
    console = Console()
    tree = Tree("TaskCrafter Jobs")

    for job in jobs:
        node = tree.add(f"[bold green]{job.id}[/bold green]: {job.name}")
        for dep in job.depends_on or []:
            node.add(f"[dim]depends_on: {dep}[/dim]")
        for succ in job.on_success or []:
            node.add(f"[green]on_success: {succ}[/green]")
        for fail in job.on_failure or []:
            node.add(f"[red]on_failure: {fail}[/red]")

    console.print(tree)
