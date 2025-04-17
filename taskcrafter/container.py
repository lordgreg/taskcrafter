from taskcrafter.exceptions.container import ContainerError, ContainerExecutionError
from taskcrafter.models.job import Job
from taskcrafter.logger import app_logger
import docker

# constant for docker timeout
DOCKER_TIMEOUT = 10


def run_job_in_docker(job: Job, params: dict = None):
    try:
        docker_client = docker.DockerClient(
            base_url=job.container.get_engine_url(),
            version="auto",
            timeout=DOCKER_TIMEOUT,
        )

        container = docker_client.containers.run(
            job.container.image,
            command=job.container.command,
            volumes=job.container.volumes or {},
            environment=params,
            detach=True,
            privileged=job.container.privileged,
            user=job.container.user,
        )

        container.wait()

        logs = container.logs()
        print(logs.decode())

        exit_code = container.wait()["StatusCode"]

        if exit_code != 0:
            raise ContainerExecutionError(
                f"Container execution failed with exit code {exit_code}"
            )

        return logs.decode()
    except docker.errors.DockerException as e:
        app_logger.error(f"Container execution failed: {e}")
        raise ContainerError(e)
    finally:
        if container is not None:
            container.remove()
