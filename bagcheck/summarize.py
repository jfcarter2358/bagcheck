import rich
from bagcheck.concourse.pipeline import Pipeline

def _print_action_summary(actions: list) -> None:
    for action in actions:
        if isinstance(action, list):
            rich.print(f'      - [yellow]Parallel[/yellow]')
            for parallel_action in action:
                rich.print(f'          - {parallel_action}')
        else:
            rich.print(f'      - {action}')

def print_summary(doc: str) -> None:
    pipeline = Pipeline(doc)

    summary = pipeline.get_summary()

    for job in summary:
        rich.print(f'[bold blue]{job}[/bold blue]')
        if len(summary[job]['triggered']) > 0:
            rich.print('    [bold yellow]Triggered By[/bold yellow]')
            for trigger in summary[job]['triggered']:
                rich.print(f'      - Change to [magenta]{trigger}[/magenta]')
        rich.print('    [bold yellow]Actions[/bold yellow]')
        _print_action_summary(summary[job]['actions'])
        if len(summary[job]['success']) > 0:
            rich.print('    [bold yellow]On [green]Success[/green][/bold yellow]')
            _print_action_summary(summary[job]['success'])
        if len(summary[job]['error']) > 0:
            rich.print('    [bold yellow]On [red]Error[/red][/bold yellow]')
            _print_action_summary(summary[job]['error'])
        if len(summary[job]['failure']) > 0:
            rich.print('    [bold yellow]On [red]Failure[/red][/bold yellow]')
            _print_action_summary(summary[job]['failure'])
        if len(summary[job]['triggers']) > 0:
            rich.print('    [bold yellow]Triggers[/bold yellow]')
            for trigger in summary[job]['triggers']:
                rich.print(f'      - [blue]{trigger}[/blue]')
