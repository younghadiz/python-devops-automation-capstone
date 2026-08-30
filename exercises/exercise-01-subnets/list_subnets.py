import boto3
from botocore.exceptions import BotoCoreError, ClientError


def list_default_subnets() -> None:
    """
    Get all subnets in the configured/default AWS region and print
    subnet IDs that belong to the default VPC configuration.
    """

    ec2_client = boto3.client("ec2")

    try:
        response = ec2_client.describe_subnets()

        default_subnets = [
            subnet
            for subnet in response["Subnets"]
            if subnet.get("DefaultForAz", False)
        ]

        if not default_subnets:
            print("No default subnets found in the configured AWS region.")
            return

        print("Default subnet IDs:")

        for subnet in default_subnets:
            print(subnet["SubnetId"])

    except (BotoCoreError, ClientError) as error:
        print(f"Failed to retrieve AWS subnets: {error}")
        raise


if __name__ == "__main__":
    list_default_subnets()