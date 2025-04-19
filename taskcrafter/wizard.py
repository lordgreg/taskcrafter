import pathlib
import click

from taskcrafter.models.wizard import WizardEntry

TEMPLATE_DIR = "examples/jobs"


TEMPLATE_MAP: list[WizardEntry] = [
    WizardEntry("simple", "Simple setup"),
    WizardEntry("containers", "Using containers"),
    WizardEntry("jobs_with_hooks", "Using hooks"),
    WizardEntry("external_plugin", "Using external plugin"),
    WizardEntry("desktop_example", "Desktop notifications example"),
    WizardEntry("inputs_outputs", "Using inputs/outputs"),
    WizardEntry("test_build_and_deploy", "Test build and deploy"),
    WizardEntry("everything", "Everything together"),
    WizardEntry("empty_file", "Empty file"),
]


def create_file_wizard(file: pathlib.Path) -> bool:
    if click.confirm(
        f"File '{file}' does not exist. Would you like to create it?", default=True
    ):
        click.echo("What type of job template would you like?\n")
        for index, entry in enumerate(TEMPLATE_MAP):
            click.echo(f"  {index + 1}. {entry.name}")

        selected = -1
        while selected < 1 or selected > len(TEMPLATE_MAP):
            selected = int(
                click.prompt(
                    "\nEnter the number of the desired template",
                    type=click.Choice(
                        [str(i) for i in range(1, len(TEMPLATE_MAP) + 1)]
                    ),
                    default="1",
                    show_choices=False,
                    show_default=True,
                )
            )

        template_name = TEMPLATE_MAP[int(selected) - 1].name
        template_file = pathlib.Path(TEMPLATE_DIR) / f"{template_name}.yaml"

        if not template_file.exists():
            click.echo(f"Template '{template_name}' not found.")
            return False

        directory = file.parent
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)

        file.write_text(template_file.read_text())
        click.echo(f"Created file '{file}' using template '{template_name}'.")

        return True

    return False
