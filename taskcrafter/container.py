from taskcrafter.logger import app_logger
import docker


def run_job_in_docker(job, params):
    # docker_client = docker.from_env()
    docker_client = docker.DockerClient(
        base_url=job.container.get_engine_url(), version="auto"
    )  # Docker client

    try:
        # Ustvari in zaženi container
        container = docker_client.containers.run(
            job.container.image,
            command=job.container.command,  # Primer ukaza za zagon
            # volumes={
            #     "/path/to/job/data": {"bind": "/app/data", "mode": "rw"}
            # },  # Nastavitve mapiranja
            environment={"JOB_PARAMS": params},  # Posredovanje parametrov
            detach=True,  # Zaženi v ozadju
        )

        # Počakaj, da se job konča
        container.wait()  # Čaka na zaključek

        # Preberi izhod
        logs = container.logs()
        print(logs.decode())

        # Preveri izhodno kodo
        exit_code = container.wait()["StatusCode"]

        return exit_code, logs.decode()
    except docker.errors.DockerException as e:
        app_logger(f"Napaka pri delu z Dockerjem: {e}")
        raise e
    finally:
        # Poskrbi za čiščenje
        container.remove()
