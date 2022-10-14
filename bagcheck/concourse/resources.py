import re
import jsonpath_ng as jsonpath

messages = {
    'docker-image': {
        'get': 'Pull [yellow]${resource.source.repository}:${resource.source.tag}[/yellow]',
        'put': 'Push [yellow]${resource.source.repository}:${resource.source.tag}[/yellow]'
    },
    'git': {
        'get': 'Clone [yellow]${resource.source.uri}[/yellow] with branch [yellow]${resource.source.branch}[/yellow]',
        'put': 'Push to [yellow]${resource.source.uri}[/yellow] with branch [yellow]${resource.source.branch}[/yellow]',
    },
    'time': {
        'get': 'Run on [yellow]${resource.source.days}[/yellow] from [yellow]${resource.source.start}[/yellow] to [yellow]${resource.source.stop}[/yellow]',
        'put': 'None'
    },
    'slack-alert-notification': {
        'get': None,
        'put': 'Send Slack notification to [yellow]${resource.source.channel}[/yellow]'
    },
    'pull-request': {
        'get': 'Clone [yellow]${resource.source.repository}[/yellow] from pull request',
        'put': 'Set [yellow]${resource.source.repository}[/yellow] PR status to [yellow]${params.status}[/yellow]'
    },
    "semver": {
        'get': 'Get version of [magenta]${resource.name}[/magenta]',
        'put': 'Bump version of [magenta]${resource.name}[/magenta]'
    },
    's3-bucket': {
        'get': 'Pull down artifacts from [yellow]${resource.source.bucket}[/yellow] bucket',
        'put': 'Upload artifacts to [yellow]${resource.source.bucket}[/yellow] bucket'
    }
}

class Resources:
    def __init__(self, doc: dict):
        self.doc = doc

    def _get_resource_by_name(self, name: str) -> dict:
        for resource in self.doc['resources']:
            if resource['name'] == name:
                return resource
            
        raise KeyError(f"Resource with name {name} not found")

    def get_summary(self, obj: dict) -> tuple[list, list, list]:
        triggered = []
        actions = []
        changes = []

        action = 'get'
        if 'put' in obj:
            action = 'put'
            changes.append(obj['put'])
        else:
            if 'trigger' in obj:
                if obj['trigger']:
                    triggered.append(obj['get'])

        resource = self._get_resource_by_name(obj[action])
        if not resource['type'] in messages:
            message = f'[GENERIC] Perform {action} on resource [magenta]{resource["name"]}[/magenta] of type [yellow]{resource["type"]}[/yellow]'
        else:
            message = messages[resource['type']][action]
            replacements = re.findall(r'\$\{[^ \t\$]*\}', message)
            for replacement in replacements:
                key_string = replacement[2:-1]
                if key_string.startswith('resource'):
                    jsonpath_key = f'${key_string[8:]}'
                    jsonpath_expression = jsonpath.parse(jsonpath_key)
                    value = jsonpath_expression.find(resource)[0].value
                    if isinstance(value, list):
                        value = ', '.join(value)
                    message = message.replace(replacement, value)
                elif key_string.startswith('params'):
                    jsonpath_key = f'${key_string[6:]}'
                    jsonpath_expression = jsonpath.parse(jsonpath_key)
                    value = jsonpath_expression.find(obj['params'])[0].value
                    if isinstance(value, list):
                        value = ', '.join(value)
                    message = message.replace(replacement, value)
        actions.append(message)

        return triggered, actions, changes

    def get_pr_puts(self, obj: dict) -> list:
        pr_puts = []

        if 'get' in obj:
            return []

        resource = self._get_resource_by_name(obj['put'])
        if resource['type'] == 'pull-request':
            pr_puts.append(obj)
            return pr_puts

        return []
