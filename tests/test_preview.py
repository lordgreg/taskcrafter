from taskcrafter.preview import rich_preview


def test_rich_preview():
    call = rich_preview([])
    assert call is None


def test_rich_preview_with_jobs():
    from taskcrafter.models.job import Job

    job1 = Job(id="job1", name="Job 1", enabled=True)
    job2 = Job(id="job2", name="Job 2", enabled=False)
    job3 = Job(id="job3", name="Job 3", enabled=True)

    job1.depends_on = ["job2"]
    job1.on_success = ["job3"]
    job1.on_failure = ["job2"]
    job1.on_finish = ["job3"]
    job1.timeout = 10
    job1.max_retries.count = 5
    job1.max_retries.interval = 15

    call = rich_preview([job1, job2, job3])
    assert call is None
