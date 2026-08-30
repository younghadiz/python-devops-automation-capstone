import os
from operator import itemgetter

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv


load_dotenv()

REPOSITORY_NAME = os.getenv(
    "ECR_REPO_NAME",
    "python-devops-demo-app",
)

ecr_client = boto3.client("ecr")


def list_repositories() -> None:
    paginator = ecr_client.get_paginator("describe_repositories")

    repositories = []

    for page in paginator.paginate():
        repositories.extend(page["repositories"])

    if not repositories:
        print("No ECR repositories found.")
        return

    print("ECR repositories:")
    for repository in repositories:
        print(repository["repositoryName"])


def list_images_sorted() -> None:
    response = ecr_client.describe_images(
        repositoryName=REPOSITORY_NAME
    )

    tagged_images = []

    for image in response["imageDetails"]:
        image_tags = image.get("imageTags", [])

        for tag in image_tags:
            tagged_images.append(
                {
                    "tag": tag,
                    "pushed_at": image["imagePushedAt"],
                }
            )

    images_sorted = sorted(
        tagged_images,
        key=itemgetter("pushed_at"),
        reverse=True,
    )

    print(
        f"\nImages in repository '{REPOSITORY_NAME}' "
        f"(newest first):"
    )

    for image in images_sorted:
        print(
            f"tag={image['tag']} "
            f"pushed_at={image['pushed_at']}"
        )


def main() -> None:
    try:
        list_repositories()
        list_images_sorted()

    except (BotoCoreError, ClientError) as error:
        print(f"ECR operation failed: {error}")
        raise


if __name__ == "__main__":
    main()