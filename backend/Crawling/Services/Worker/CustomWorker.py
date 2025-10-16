from rq import Worker
from Services.Worker.worker_hooks import on_start, on_success, on_failure

class CustomWorker(Worker):
    def execute_job(self, job, queue):
        job.meta['on_start'] = on_start
        job.meta['on_success'] = on_success
        job.meta['on_failure'] = on_failure
        job.save_meta()
        return super().execute_job(job, queue)

    def on_job_start(self, job, *args, **kwargs):
        hook = job.meta.get('on_start')
        if hook:
            hook(job)

    def on_job_success(self, job, *args, **kwargs):
        hook = job.meta.get('on_success')
        if hook:
            hook(job)

    def on_job_failure(self, job, exc_type, exc_value, traceback):
        hook = job.meta.get('on_failure')
        if hook:
            hook(job, exc_type, exc_value, traceback)