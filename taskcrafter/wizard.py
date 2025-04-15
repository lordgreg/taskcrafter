import pathlib
import click

TEMPLATE_DIR = "examples/jobs"

TEMPLATE_MAP: dict[str, dict[str, str]] = {
    "1": {"simple": "Simple setup"},
    "2": {"containers": "Using containers"},
    "3": {"jobs_with_hooks": "Using hooks"},
    "4": {"external_plugin": "Using external plugin"},
    "5": {"desktop_example": "Desktop notifications example"},
    "6": {"inputs_outputs": "Using inputs/outputs"},
    "7": {"test_build_and_deploy": "Test build and deploy"},
    "8": {"empty_file": "Empty file"},
}


def create_file_wizard(file: pathlib.Path) -> bool:
    if click.confirm(
        f"File '{file}' does not exist. Would you like to create it?", default=True
    ):
        click.echo("What type of job template would you like?\n")
        for key, template in TEMPLATE_MAP.items():
            click.echo(f"  {key}. {list(template.values())[0].title()}")

        selected = -1
        while selected not in TEMPLATE_MAP:
            selected = click.prompt(
                "\nEnter the number of the desired template",
                type=click.Choice(TEMPLATE_MAP.keys()),
                default="1",
                show_choices=False,
                show_default=True,
            )

        template_name = list(TEMPLATE_MAP[selected].keys())[0]
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
