from taskcrafter.logger import app_logger
import docker

# constant for docker timeout
DOCKER_TIMEOUT = 10


def run_job_in_docker(job, params: dict = None):
    try:
        docker_client = docker.DockerClient(
            base_url=job.container.get_engine_url(),
            version="auto",
            timeout=DOCKER_TIMEOUT,
        )

        container = docker_client.containers.run(
            job.container.image,
            command=job.container.command,
            # volumes={
            #     "/path/to/job/data": {"bind": "/app/data", "mode": "rw"}
            # },
            environment=params,
            detach=True,
        )

        container.wait()

        logs = container.logs()
        print(logs.decode())

        exit_code = container.wait()["StatusCode"]

        return exit_code, logs.decode()
    except docker.errors.DockerException as e:
        app_logger.error(f"Container execution failed: {e}")
        raise e
    finally:
        container.remove()
