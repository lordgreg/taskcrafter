from taskcrafter.container import run_job_in_docker
from taskcrafter.models.job import Job
from unittest.mock import patch, MagicMock
from docker import DockerClient
from docker.models.containers import Container


@patch("taskcrafter.container.docker.DockerClient")
def test_run_job_in_docker(mock_docker_client):
    """
    Test with mocked Container
    """

    # Test the run_job_in_docker function
    job = Job(
        **{
            "id": "test_job",
            "name": "Test Job",
            "container": {
                "engine": "podman",
                "image": "alpine",
                "command": "echo Hello World",
                "volumes": {},
                "privileged": False,
                "user": None,
            },
            "params": {},
        }
    )

    mock_client_instance = MagicMock(spec=DockerClient)
    mock_container_instance = MagicMock(spec=Container)
    mock_docker_client.return_value = mock_client_instance
    mock_client_instance.containers.run.return_value = mock_container_instance

    mock_container_instance.wait.return_value = {"StatusCode": 0}
    mock_container_instance.logs.return_value = b"Hello World"

    exit_code, logs = run_job_in_docker(job, {})

    mock_docker_client.assert_called_once_with(
        base_url=job.container.get_engine_url(),
        version="auto",
        timeout=10,
    )

    mock_client_instance.containers.run.assert_called_once_with(
        job.container.image,
        command=job.container.command,
        volumes=job.container.volumes,
        environment=job.params,
        detach=True,
        privileged=job.container.privileged,
        user=job.container.user,
    )

    # Assert the mocked container.wait() and container.logs() were called
    # mock_container_instance.wait.assert_called_once()
    mock_container_instance.logs.assert_called_once()

    assert exit_code == 0
    assert logs == "Hello World"
