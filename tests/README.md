# BagCheck

## About

`bagcheck` is a relatively simply command line utility developed to make validating Concourse pipelines simpler. To accomplish this, `bagcheck` has the following functionality:

## Checking a pipeline

To check your pipeline, simply run:

```bash
bagcheck check -f /path/to/your/concourse/pipeline.yaml
```

at which point `bagcheck` will proceed to check for the following conditions:

- All git resources are pointed at the `main` branch
- All PR resource puts in the same job have the same context
- All PR statuses are accounted for in a job (success, failure, error, pending)
- All jobs have a timeout set

### Disabling Specific Checks

Sometimes you want to skip a check across the board (e.g. you don't want timeouts in a specific pipeline) or you only want to disable a check for a specific job/resource. To do this, you'll use a `.bagcheck` file. 

An example file looks something like this:

```yaml
disable:
  global:
    - check-main-branch
    - ...
  local:
    - path: '$.jobs[?(@.name = "job-name-1")]'
      tests:
        - check-pr-statuses
        - ...
    - path: '$.jobs[?(@.name = "job-name-2")]'
      tests:
        - check-timeout
        - ...
    - ...
```

with any check listed under the `disable.global` key being completely disabled and the tests under each path being disabled when the job meets that JSONPath criteria (the ellipsis denote that you can include as many as you want in each section).

Currently the following tests are run and as a consequence can be disabled:

- `check-main-branch`
- `check-timeout`
- `check-pr-statuses`
- `check-pr-contexts`

One thing to note is that `bagcheck` will first attempt to read a file located at `~/.bagcheck` and then will attempt to read one at the current working directory, combining the values with whatever is located in your `~/.bagcheck` file.

## Summarizing a pipeline

Having to read through a 1000+ line YAML file can make it hard to understand what the pipeline is doing on a conceptual level as well as how everything ties together. To help with this, you can run:

```bash
bagcheck summary -f /path/to/your/concourse/pipeline.yaml
```

at which point `bagcheck` will print out a summarized version of your pipeline which attempts to:

- List in plain English what each step of a job does
- Describe what resource changes will cause the job to trigger
- Describe which jobs will be triggered as a result
