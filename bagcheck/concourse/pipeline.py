from bagcheck.concourse.jobs import Jobs

class Pipeline:
    def __init__(self, doc: dict):
        self.doc = doc
        self.jobs = Jobs(doc)

    def get_summary(self) -> dict:
        summary = {}
        
        for job in self.doc['jobs']:
            triggered, actions, changes, success, error, failure = self.jobs.get_summary(job)

            summary[job['name']] = {
                'triggered': triggered,
                'actions': actions,
                'changes': changes,
                'success': success,
                'error': error,
                'failure': failure
            }

        for key_1 in summary:
            triggers = []
            for key_2 in summary:
                if key_1 == key_2:
                    continue
                for trigger in summary[key_2]['triggered']:
                    for change in summary[key_1]['changes']:
                        if change == trigger:
                            triggers.append(key_2)
            summary[key_1]['triggers'] = triggers

        for key in summary:
            summary[key]['triggers'] = list(set(summary[key]['triggers']))

        return summary

    def get_pr_puts(self):
        pr_puts = {}
        
        for job in self.doc['jobs']:
            job_pr_puts = self.jobs.get_pr_puts(job)

            pr_puts[job['name']] = job_pr_puts

        return pr_puts
