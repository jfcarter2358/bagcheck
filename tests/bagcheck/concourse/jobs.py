from bagcheck.concourse.step import Step

class Jobs:
    def __init__(self, doc: dict):
        self.doc = doc
        self.steps = Step(doc)

    def get_summary(self, obj: dict) -> tuple[list, list, list, list, list, list]:
        triggered = []
        actions = []
        changes = []
        success = []
        failure = []
        error = []

        plan_triggered, plan_actions, plan_changes = self._get_summary_from_block(obj, 'plan')
        triggered += plan_triggered
        actions += plan_actions
        changes += plan_changes

        if 'on_success' in obj:
            success_triggered, success_actions, success_changes = self._get_summary_from_block(obj, 'on_success')
            triggered += success_triggered
            success += success_actions
            changes += success_changes
        if 'on_error' in obj:
            error_triggered, error_actions, error_changes = self._get_summary_from_block(obj, 'on_error')
            triggered += error_triggered
            error += error_actions
            changes += error_changes
        if 'on_failure' in obj:
            failure_triggered, failure_actions, failure_changes = self._get_summary_from_block(obj, 'on_failure')
            triggered += failure_triggered
            failure += failure_actions
            changes += failure_changes

        return triggered, actions, changes, success, error, failure

    def _get_summary_from_block(self, obj: dict, key: str) -> list:
        triggered = []
        actions = []
        changes = []

        steps = []
        if isinstance(obj[key], dict):
            if 'do' in obj[key]:
                steps = obj[key]['do']
            else:
                steps = obj[key]
            steps = [steps]
        else:
            if 'do' in obj[key][0]:
                steps = obj[key][0]['do']
            else:
                steps = obj[key]

        if isinstance(steps, dict):
            steps = [steps]
        
        for step in steps:
            step_triggered, step_actions, step_changes = self.steps.get_summary(step)
            triggered += step_triggered
            actions += step_actions
            changes += step_changes

        return triggered, actions, changes

    def _get_pr_puts_from_block(self, obj: dict, key: str) -> list:
        pr_puts = []

        steps = []
        if isinstance(obj[key], dict):
            if 'do' in obj[key]:
                steps = obj[key]['do']
            else:
                steps = obj[key]
            steps = [steps]
        else:
            if 'do' in obj[key][0]:
                steps = obj[key][0]['do']
            else:
                steps = obj[key]
            
        for step in steps:
            step_pr_puts = self.steps.get_pr_puts(step)
            pr_puts += step_pr_puts

        return pr_puts

    def get_pr_puts(self, obj: dict) -> list:
        pr_puts = []

        pr_puts += self._get_pr_puts_from_block(obj, 'plan')

        if 'on_success' in obj:
            pr_puts += self._get_pr_puts_from_block(obj, 'on_success')
        if 'on_error' in obj:
            pr_puts += self._get_pr_puts_from_block(obj, 'on_error')
        if 'on_failure' in obj:
            pr_puts += self._get_pr_puts_from_block(obj, 'on_failure')

        return pr_puts


    