import logging
import jsonpath_ng as jsonpath
import jsonpath_ng.ext as jsonpath_ext
from bagcheck.concourse.pipeline import Pipeline

def _check_skip(parent_key: str, obj: dict, ignore: dict, test_name: str) -> bool:
    test_json = {parent_key:[obj]}
    should_skip = False
    for local_disable in ignore:
        jsonpath_key = local_disable['path']
        jsonpath_expression = jsonpath_ext.parse(jsonpath_key)
        if jsonpath_expression.find(test_json):
            if test_name in local_disable['tests']:
                should_skip = True
    return should_skip

def check_main_branch(doc: dict, log: logging.Logger, ignore: dict):
    issue_count = 0

    if 'resources' in doc:
        log.info("Checking git resource branches...")
        for resource in doc['resources']:
            if _check_skip('resources', resource, ignore, 'check-main-branch'):
                continue
            if resource['type'] == 'git':
                log.debug(f'Checking git resource [magenta]{resource["name"]}[/magenta]', extra={"markup": True})
                if resource['source']['branch'] != 'main':
                    log.error(f'Resource [magenta]{resource["name"]}[/magenta] is pointed at branch [red]{resource["source"]["branch"]}[/red], not [green]main[/green]', extra={"markup": True})
                    # if not ignore_warnings:
                    issue_count += 1
            else:
                log.debug(f'Resource [magenta]{resource["name"]}[/magenta] is not of type [yellow]git[/yellow], skipping', extra={"markup": True})
        log.info("Done!")
    else:
        log.warning("No resources to check")

    return issue_count

def check_timeout(doc: dict, log: logging.Logger, ignore: list) -> int:
    issue_count = 0
    
    if 'jobs' in doc:
        log.info("Checking jobs have timeouts set...")
        for job in doc['jobs']:
            if _check_skip('jobs', job, ignore, 'check-timeout'):
                continue
            name = job['name']
            plan = job['plan']
            if not 'timeout' in plan[0]:
                log.error(f'Job [cyan]{name}[/cyan] has no timeout set', extra={"markup": True})
                # if not ignore_warnings:
                issue_count += 1
        log.info("Done!")
    else:
        log.warning('No jobs to check')

    return issue_count

def check_pr_contexts(doc: dict, log: logging.Logger, ignore: dict) -> int:
    issue_count = 0

    if 'jobs' in doc:

        log.info("Checking that all jobs with PR puts have consistent contexts...")

        pipeline = Pipeline(doc)
        pr_puts = pipeline.get_pr_puts()

        for job in pr_puts:
            if _check_skip('jobs', job, ignore, 'check-pr-contexts'):
                continue
            context = ''
            
            for put in pr_puts[job]:
                if not context:
                    context = put['params']['context']
                elif context != put['params']['context']:
                    issue_count += 1
                    log.error(f'Job [cyan]{job}[/cyan] has multiple PR status contexts: [yellow]{context}[/yellow], [yellow]{put["params"]["context"]}[/yellow]', extra={"markup": True})

        log.info("Done!")
    else:
        log.warning('No jobs to check')
                
    return issue_count

def check_pr_statuses(doc: dict, log: logging.Logger, ignore: dict) -> int:
    issue_count = 0

    if 'jobs' in doc:

        log.info("Checking that all jobs with PR puts account for all statuses...")

        pipeline = Pipeline(doc)
        pr_puts = pipeline.get_pr_puts()

        for job in pr_puts:
            
            jsonpath_expression = jsonpath_ext.parse(f'$.jobs[?(name = "{job}")]')
            job_json = jsonpath_expression.find(doc)[0].value
            if _check_skip('jobs', job_json, ignore, 'check-pr-statuses'):
                continue

            has_pending = False
            has_success = False
            has_error = False
            has_failure = False
            
            for put in pr_puts[job]:
                if put['params']['status'] == 'pending':
                    has_pending = True
                if put['params']['status'] == 'success':
                    has_success = True
                if put['params']['status'] == 'error':
                    has_error = True
                if put['params']['status'] == 'failure':
                    has_failure = True

            if (has_pending or has_failure or has_error or has_success):
                if not has_success:
                    issue_count += 1
                    log.error(f'Job [cyan]{job}[/cyan] is missing PR push for [yellow]success[/yellow] status', extra={"markup": True})
                if not has_pending:
                    issue_count += 1
                    log.error(f'Job [cyan]{job}[/cyan] is missing PR push for [yellow]pending[/yellow] status', extra={"markup": True})
                if not has_failure:
                    issue_count += 1
                    log.error(f'Job [cyan]{job}[/cyan] is missing PR push for [yellow]failure[/yellow] status', extra={"markup": True})
                if not has_error:
                    issue_count += 1
                    log.error(f'Job [cyan]{job}[/cyan] is missing PR push for [yellow]error[/yellow] status', extra={"markup": True})

        log.info("Done!")
    else:
        log.warning('No jobs to check')
                
    return issue_count

TEST_MAPPING = {
    "check-main-branch": check_main_branch,
    'check-timeout': check_timeout,
    'check-pr-contexts': check_pr_contexts,
    'check-pr-statuses': check_pr_statuses
}
