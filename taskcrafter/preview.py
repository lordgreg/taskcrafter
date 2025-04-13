from rich.tree import Tree
from rich.console import Console
from taskcrafter.models.job import Job

console = Console()


def rich_preview(jobs: list[Job]):
    tree = Tree("[bold green]TaskCrafter Job Preview")

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

        if job.max_retries and (
            job.max_retries.count > 0 or job.max_retries.interval > 0
        ):
            job_branch.add(
                f"Retries: [bold]{job.max_retries.count}[/] every "
                f"[bold]{job.max_retries.interval}s[/]"
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
