from rich.tree import Tree
from rich.table import Table
from rich.console import Console
from rich.text import Text
from taskcrafter.models.job import Job, JobStatus

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


def result_table(jobs: list[Job]):
    console = Console()
    table = Table(title="Job Execution Summary")

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Status", style="bold")
    table.add_column("Retries", style="bold")
    table.add_column("Duration", style="bold")

    for job in jobs:
        match job.result.status:
            case JobStatus.ERROR:
                status = Text(job.result.get_status().value, "red")
            case JobStatus.SUCCESS:
                status = Text(job.result.get_status().value, "green")
            case _:
                status = job.result.get_status().value

        table.add_row(
            str(job.id),
            job.name,
            status,
            str(job.result.retries),
            f"{job.result.get_elapsed_time():.3f}s",
        )

    console.print(table)
