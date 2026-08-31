import os
from operator import itemgetter

import boto3


repository_name = os.environ["ECR_REPO_NAME"]

ecr_client = boto3.client("ecr")

response = ecr_client.describe_images(
    repositoryName=repository_name
)

images = []

for image in response["imageDetails"]:
    for tag in image.get("imageTags", []):
        images.append(
            {
                "tag": tag,
                "pushed_at": image["imagePushedAt"],
            }
        )

images = sorted(
    images,
    key=itemgetter("pushed_at"),
    reverse=True,
)

for image in images:
    print(image["tag"])