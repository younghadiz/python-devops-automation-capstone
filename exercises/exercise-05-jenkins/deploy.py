import base64
import os
import shlex

import boto3
import paramiko


ssh_host = os.environ["EC2_SERVER"]
ssh_user = os.environ["EC2_USER"]
ssh_private_key = os.environ["SSH_KEY_FILE"]

docker_registry = os.environ["ECR_REGISTRY"]
docker_image = os.environ["DOCKER_IMAGE"]

container_port = os.environ["CONTAINER_PORT"]
host_port = os.environ["HOST_PORT"]

aws_region = os.environ["AWS_DEFAULT_REGION"]

CONTAINER_NAME = "python-devops-app"

ecr_client = boto3.client(
    "ecr",
    region_name=aws_region,
)


def get_ecr_credentials() -> tuple[str, str]:
    response = ecr_client.get_authorization_token()

    auth_data = response["authorizationData"][0]

    decoded_token = base64.b64decode(
        auth_data["authorizationToken"]
    ).decode("utf-8")

    username, password = decoded_token.split(":", 1)

    return username, password


def execute_command(
    ssh_client: paramiko.SSHClient,
    command: str,
) -> None:
    _, stdout, stderr = ssh_client.exec_command(command)

    exit_code = stdout.channel.recv_exit_status()

    output = "".join(stdout.readlines()).strip()
    errors = "".join(stderr.readlines()).strip()

    if output:
        print(output)

    if errors:
        print(errors)

    if exit_code != 0:
        raise RuntimeError(
            f"Remote command failed with exit code "
            f"{exit_code}: {command}"
        )


def main() -> None:
    docker_user, docker_password = get_ecr_credentials()

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    ssh.connect(
        hostname=ssh_host,
        username=ssh_user,
        key_filename=ssh_private_key,
        timeout=20,
    )

    try:
        login_command = (
            f"echo {shlex.quote(docker_password)} | "
            f"docker login "
            f"{shlex.quote(docker_registry)} "
            f"--username {shlex.quote(docker_user)} "
            f"--password-stdin"
        )

        execute_command(
            ssh,
            login_command,
        )

        execute_command(
            ssh,
            f"docker pull {shlex.quote(docker_image)}",
        )

        execute_command(
            ssh,
            f"docker rm -f {CONTAINER_NAME} "
            f"2>/dev/null || true",
        )

        run_command = (
            "docker run -d "
            f"--name {CONTAINER_NAME} "
            "--restart unless-stopped "
            f"-p {host_port}:{container_port} "
            f"{shlex.quote(docker_image)}"
        )

        execute_command(
            ssh,
            run_command,
        )

        print(
            f"Deployment completed: {docker_image}"
        )

    finally:
        ssh.close()


if __name__ == "__main__":
    main()