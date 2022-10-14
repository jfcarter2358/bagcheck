from bagcheck.concourse.resources import Resources
from bagcheck.concourse.task import Task

class Step:
    def __init__(self, doc: dict):
        self.doc = doc
        self.resources = Resources(doc)
        self.task = Task(doc)

    def get_summary(self, obj: dict) -> tuple[list, list, list]:
        triggered = []
        actions = []
        changes = []

        if 'in_parallel' in obj:
            if 'steps' in obj['in_parallel']:
                parallel_actions = []
                for step in obj['in_parallel']['steps']:
                    parallel_step_triggered, parallel_step_actions, parallel_step_changes = self.get_summary(step)
                    triggered += parallel_step_triggered
                    parallel_actions += parallel_step_actions
                    changes += parallel_step_changes
                actions.append(parallel_actions)
            else:
                parallel_actions = []
                for step in obj['in_parallel']:
                    parallel_step_triggered, parallel_step_actions, parallel_step_changes = self.get_summary(step)
                    triggered += parallel_step_triggered
                    parallel_actions += parallel_step_actions
                    changes += parallel_step_changes
                actions.append(parallel_actions)
        elif 'get' in obj:
            get_triggered, get_actions, get_changes = self.resources.get_summary(obj)
            triggered += get_triggered
            actions += get_actions
            changes += get_changes
        elif 'put' in obj:
            put_triggered, put_actions, put_changes = self.resources.get_summary(obj)
            triggered += put_triggered
            actions += put_actions
            changes += put_changes
        elif 'task' in obj:
            task_triggered, task_actions, task_changes = self.task.get_summary(obj)
            triggered += task_triggered
            actions += task_actions
            changes += task_changes

        return triggered, actions, changes

    def get_pr_puts(self, obj: dict) -> list:
        pr_puts = []

        if 'in_parallel' in obj:
            if 'steps' in obj['in_parallel']:
                for step in obj['in_parallel']['steps']:
                    parallel_pr_puts = self.get_pr_puts(step)
                    pr_puts += parallel_pr_puts
            else:
                for step in obj['in_parallel']:
                    parallel_pr_puts = self.get_pr_puts(step)
                    pr_puts += parallel_pr_puts
        elif 'put' in obj:
            put_pr_puts = self.resources.get_pr_puts(obj)
            pr_puts += put_pr_puts

        return pr_puts
