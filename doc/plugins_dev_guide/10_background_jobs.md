# Background Jobs - NetBox OSS
This feature was introduced in NetBox v4.1.

NetBox plugins can defer certain operations by enqueuing [background jobs](https://netboxlabs.com/docs/netbox/en/stable/features/background-jobs/), which are executed asynchronously by background workers. This is helpful for decoupling long-running processes from the user-facing request-response cycle.

For example, your plugin might need to fetch data from a remote system. Depending on the amount of data and the responsiveness of the remote server, this could take a few minutes. Deferring this task to a queued job ensures that it can be completed in the background, without interrupting the user. The data it fetches can be made available once the job has completed.

Job Runners
-----------

A background job implements a basic [Job](https://netboxlabs.com/docs/netbox/en/stable/models/core/job/) executor for all kinds of tasks. It has logic implemented to handle the management of the associated job object, rescheduling of periodic jobs in the given interval and error handling. Adding custom jobs is done by subclassing NetBox's `JobRunner` class.

### `JobRunner (ABC)`

Background Job helper class.

This class handles the execution of a background job. It is responsible for maintaining its state, reporting errors, and scheduling recurring jobs.

#### `__init__(self, job)` `special`

**Parameters:**


|Name|Type|Description                                  |Default |
|----|----|---------------------------------------------|--------|
|job |    |The specific Job this JobRunner is executing.|required|


#### `run(self, *args, **kwargs)`

Run the job.

A `JobRunner` class needs to implement this method to execute all commands of the job.

#### `handle(job, *args, **kwargs)` `classmethod`

Handle the execution of a `Job`.

This method is called by the Job Scheduler to handle the execution of all job commands. It will maintain the job's metadata and handle errors. For periodic jobs, a new job is automatically scheduled using its `interval`.

#### `get_jobs(instance=None)` `classmethod`

Get all jobs of this `JobRunner` related to a specific instance.

#### `enqueue(*args, **kwargs)` `classmethod`

Enqueue a new `Job`.

This method is a wrapper of `Job.enqueue()` using `handle()` as function callback. See its documentation for parameters.

#### `enqueue_once(cls, instance=None, schedule_at=None, interval=None, *args, **kwargs)` `classmethod`

Enqueue a new `Job` once, i.e. skip duplicate jobs.

Like `enqueue()`, this method adds a new `Job` to the job queue. However, if there's already a job of this class scheduled for `instance`, the existing job will be updated if necessary. This ensures that a particular schedule is only set up once at any given time, i.e. multiple calls to this method are idempotent.

Note that this does not forbid running additional jobs with the `enqueue()` method, e.g. to schedule an immediate synchronization job in addition to a periodic synchronization schedule.

For additional parameters see `enqueue()`.

**Parameters:**


|Name       |Type|Description                                                |Default|
|-----------|----|-----------------------------------------------------------|-------|
|instance   |    |The NetBox object to which this job pertains (optional)    |None   |
|schedule_at|    |Schedule the job to be executed at the passed date and time|None   |
|interval   |    |Recurrence interval (in minutes)                           |None   |


#### Example

jobs.py

```
from netbox.jobs import JobRunner


class MyTestJob(JobRunner):
    class Meta:
        name = "My Test Job"

    def run(self, *args, **kwargs):
        obj = self.job.object
        # your logic goes here

```


You can schedule the background job from within your code (e.g. from a model's `save()` method or a view) by calling `MyTestJob.enqueue()`. This method passes through all arguments to `Job.enqueue()`. However, no `name` argument must be passed, as the background job name will be used instead.

### Attributes

`JobRunner` attributes are defined under a class named `Meta` within the job. These are optional, but encouraged.

#### `name`

This is the human-friendly names of your background job. If omitted, the class name will be used.

### Scheduled Jobs

As described above, jobs can be scheduled for immediate execution or at any later time using the `enqueue()` method. However, for management purposes, the `enqueue_once()` method allows a job to be scheduled exactly once avoiding duplicates. If a job is already scheduled for a particular instance, a second one won't be scheduled, respecting thread safety. An example use case would be to schedule a periodic task that is bound to an instance in general, but not to any event of that instance (such as updates). The parameters of the `enqueue_once()` method are identical to those of `enqueue()`.

Tip

It is not forbidden to `enqueue()` additional jobs while an interval schedule is active. An example use of this would be to schedule a periodic daily synchronization, but also trigger additional synchronizations on demand when the user presses a button.

#### Example

jobs.py

```
from netbox.jobs import JobRunner


class MyHousekeepingJob(JobRunner):
    class Meta:
        name = "Housekeeping"

    def run(self, *args, **kwargs):
        # your logic goes here

```


\_\_init\_\_.py

```
from netbox.plugins import PluginConfig

class MyPluginConfig(PluginConfig):
    def ready(self):
        from .jobs import MyHousekeepingJob
        MyHousekeepingJob.setup(interval=60)

```


Task queues
-----------

Three task queues of differing priority are defined by default:

*   High
*   Default
*   Low

Any tasks in the "high" queue are completed before the default queue is checked, and any tasks in the default queue are completed before those in the "low" queue.

Plugins can also add custom queues for their own needs by setting the `queues` attribute under the PluginConfig class. An example is included below:

```
class MyPluginConfig(PluginConfig):
    name = 'myplugin'
    ...
    queues = [
        'foo',
        'bar',
    ]

```


The `PluginConfig` above creates two custom queues with the following names `my_plugin.foo` and `my_plugin.bar`. (The plugin's name is prepended to each queue to avoid conflicts between plugins.)

Configuring the RQ worker process

By default, NetBox's RQ worker process only services the high, default, and low queues. Plugins which introduce custom queues should advise users to either reconfigure the default worker, or run a dedicated worker specifying the necessary queues. For example:

```
python manage.py rqworker my_plugin.foo my_plugin.bar

```

