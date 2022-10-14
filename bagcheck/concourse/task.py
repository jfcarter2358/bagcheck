class Task:
    def __init__(self, doc: dict):
        self.doc = doc

    def get_summary(self, obj: dict) -> tuple[list, list, list]:
        triggered = []
        actions = []
        changes = []

        actions.append(f'Run [cyan]{obj["task"]}[/cyan] task')

        return triggered, actions, changes


    