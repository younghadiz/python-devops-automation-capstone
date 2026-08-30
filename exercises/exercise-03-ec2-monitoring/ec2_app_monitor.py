import os
import time

import boto3
import paramiko
import requests
import schedule
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv


load_dotenv()

REGION = os.getenv("AWS_DEFAULT_REGION", "eu-central-1")
KEY_NAME = os.environ["EC2_KEY_NAME"]
PRIVATE_KEY_PATH = os.environ["EC2_PRIVATE_KEY_PATH"]
SSH_ALLOWED_CIDR = os.environ["SSH_ALLOWED_CIDR"]

INSTANCE_NAME = "python-devops-monitoring-server"
INSTANCE_TYPE = "t3.micro"
SSH_USER = "ec2-user"

APPLICATION_PORT = 8080
CONTAINER_NAME = "nginx-monitor"

MONITOR_INTERVAL_SECONDS = 10
FAILURE_THRESHOLD = 5

ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)
ssm_client = boto3.client("ssm", region_name=REGION)

app_not_accessible_count = 0
ssh_host = ""


def get_latest_amazon_linux_ami() -> str:
    response = ssm_client.get_parameter(
        Name="/aws/service/ami-amazon-linux-latest/"
             "al2023-ami-kernel-default-x86_64"
    )
    return response["Parameter"]["Value"]


def get_default_vpc_id() -> str:
    response = ec2_client.describe_vpcs(
        Filters=[
            {
                "Name": "is-default",
                "Values": ["true"],
            }
        ]
    )

    if not response["Vpcs"]:
        raise RuntimeError("No default VPC found.")

    return response["Vpcs"][0]["VpcId"]


def ensure_security_group(vpc_id: str) -> str:
    group_name = "python-devops-monitoring-sg"

    response = ec2_client.describe_security_groups(
        Filters=[
            {
                "Name": "group-name",
                "Values": [group_name],
            },
            {
                "Name": "vpc-id",
                "Values": [vpc_id],
            },
        ]
    )

    if response["SecurityGroups"]:
        return response["SecurityGroups"][0]["GroupId"]

    response = ec2_client.create_security_group(
        GroupName=group_name,
        Description="Security group for Python EC2 monitoring capstone",
        VpcId=vpc_id,
    )

    group_id = response["GroupId"]

    ec2_client.authorize_security_group_ingress(
        GroupId=group_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [
                    {
                        "CidrIp": SSH_ALLOWED_CIDR,
                        "Description": "Restricted SSH access",
                    }
                ],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": APPLICATION_PORT,
                "ToPort": APPLICATION_PORT,
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Public Nginx demo access",
                    }
                ],
            },
        ],
    )

    return group_id


def find_existing_instance():
    response = ec2_client.describe_instances(
        Filters=[
            {
                "Name": "tag:Name",
                "Values": [INSTANCE_NAME],
            },
            {
                "Name": "instance-state-name",
                "Values": [
                    "pending",
                    "running",
                    "stopping",
                    "stopped",
                ],
            },
        ]
    )

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            return instance

    return None


def create_or_get_instance() -> str:
    existing_instance = find_existing_instance()

    if existing_instance:
        print("Instance already exists.")
        instance_id = existing_instance["InstanceId"]

        if existing_instance["State"]["Name"] == "stopped":
            print("Starting existing stopped instance.")
            ec2_client.start_instances(InstanceIds=[instance_id])

        return instance_id

    print("Creating a new EC2 instance.")

    ami_id = get_latest_amazon_linux_ami()
    vpc_id = get_default_vpc_id()
    security_group_id = ensure_security_group(vpc_id)

    instances = ec2_resource.create_instances(
        ImageId=ami_id,
        KeyName=KEY_NAME,
        MinCount=1,
        MaxCount=1,
        InstanceType=INSTANCE_TYPE,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": INSTANCE_NAME,
                    },
                    {
                        "Key": "Project",
                        "Value": "python-devops-automation-capstone",
                    },
                ],
            }
        ],
    )

    return instances[0].id


def wait_until_instance_ready(instance_id: str) -> None:
    print("Waiting for EC2 instance to become fully initialized.")

    while True:
        statuses = ec2_client.describe_instance_status(
            InstanceIds=[instance_id],
            IncludeAllInstances=True,
        )

        if statuses["InstanceStatuses"]:
            status = statuses["InstanceStatuses"][0]

            instance_status = status["InstanceStatus"]["Status"]
            system_status = status["SystemStatus"]["Status"]
            instance_state = status["InstanceState"]["Name"]

            print(
                f"state={instance_state}, "
                f"instance_status={instance_status}, "
                f"system_status={system_status}"
            )

            if (
                instance_state == "running"
                and instance_status == "ok"
                and system_status == "ok"
            ):
                print("EC2 instance is fully initialized.")
                return

        print("Waiting 30 seconds...")
        time.sleep(30)


def get_public_ip(instance_id: str) -> str:
    response = ec2_client.describe_instances(
        InstanceIds=[instance_id]
    )

    return response["Reservations"][0]["Instances"][0][
        "PublicIpAddress"
    ]


def wait_for_ssh(host: str) -> None:
    print("Waiting for SSH connectivity.")

    for attempt in range(1, 21):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(
                hostname=host,
                username=SSH_USER,
                key_filename=PRIVATE_KEY_PATH,
                timeout=10,
            )

            ssh.close()
            print("SSH is available.")
            return

        except Exception as error:
            print(f"SSH attempt {attempt}/20 failed: {error}")
            time.sleep(15)

    raise RuntimeError("SSH did not become available.")


def execute_remote_commands(host: str, commands: list[str]) -> None:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=host,
        username=SSH_USER,
        key_filename=PRIVATE_KEY_PATH,
        timeout=15,
    )

    try:
        for command in commands:
            print(f"Executing: {command}")

            _, stdout, stderr = ssh.exec_command(command)

            exit_code = stdout.channel.recv_exit_status()

            output = "".join(stdout.readlines()).strip()
            error_output = "".join(stderr.readlines()).strip()

            if output:
                print(output)

            if error_output:
                print(error_output)

            if exit_code != 0:
                raise RuntimeError(
                    f"Remote command failed: {command}"
                )
    finally:
        ssh.close()


def install_docker_and_nginx(host: str) -> None:
    commands = [
        "sudo dnf update -y",
        "sudo dnf install -y docker",
        "sudo systemctl enable --now docker",
        "sudo docker rm -f nginx-monitor 2>/dev/null || true",
        "sudo docker run -d "
        f"--name {CONTAINER_NAME} "
        f"-p {APPLICATION_PORT}:80 nginx:alpine",
    ]

    execute_remote_commands(host, commands)


def restart_container() -> None:
    global app_not_accessible_count

    print("Restarting Nginx container.")

    execute_remote_commands(
        ssh_host,
        [
            f"sudo docker restart {CONTAINER_NAME}",
        ],
    )

    app_not_accessible_count = 0


def monitor_application() -> None:
    global app_not_accessible_count

    url = f"http://{ssh_host}:{APPLICATION_PORT}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print("Application is running successfully.")

            # Important for "5 times in a row".
            app_not_accessible_count = 0

        else:
            app_not_accessible_count += 1

            print(
                f"Application returned HTTP {response.status_code}. "
                f"Failure {app_not_accessible_count}/"
                f"{FAILURE_THRESHOLD}."
            )

    except requests.RequestException as error:
        app_not_accessible_count += 1

        print(
            f"Application connection failed: {error}. "
            f"Failure {app_not_accessible_count}/"
            f"{FAILURE_THRESHOLD}."
        )

    if app_not_accessible_count >= FAILURE_THRESHOLD:
        restart_container()


def main() -> None:
    global ssh_host

    try:
        instance_id = create_or_get_instance()

        wait_until_instance_ready(instance_id)

        ssh_host = get_public_ip(instance_id)

        print(f"EC2 public IP: {ssh_host}")

        wait_for_ssh(ssh_host)

        install_docker_and_nginx(ssh_host)

        print(
            f"Nginx available at "
            f"http://{ssh_host}:{APPLICATION_PORT}"
        )

        schedule.every(
            MONITOR_INTERVAL_SECONDS
        ).seconds.do(monitor_application)

        print(
            f"Monitoring every {MONITOR_INTERVAL_SECONDS} seconds."
        )

        while True:
            schedule.run_pending()
            time.sleep(1)

    except (BotoCoreError, ClientError, RuntimeError) as error:
        print(f"Automation failed: {error}")
        raise


if __name__ == "__main__":
    main()