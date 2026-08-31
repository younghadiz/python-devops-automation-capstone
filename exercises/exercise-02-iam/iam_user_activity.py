import boto3
from botocore.exceptions import BotoCoreError, ClientError


def get_iam_user_activity() -> None:
    iam_client = boto3.client("iam")

    try:
        paginator = iam_client.get_paginator("list_users")

        users = []

        for page in paginator.paginate():
            users.extend(page["Users"])

        if not users:
            print("No IAM users found.")
            return

        print("IAM user activity")
        print("------------------------------")

        users_with_activity = []

        for user in users:
            username = user["UserName"]
            user_id = user["UserId"]
            password_last_used = user.get("PasswordLastUsed")

            print(f"User: {username}")

            if password_last_used:
                print(f"Password last used: {password_last_used}")
                users_with_activity.append(user)
            else:
                print("Password last used: Never / not available")

            print("------------------------------")

        if not users_with_activity:
            print("No IAM user has PasswordLastUsed information.")
            return

        most_recent_user = max(
            users_with_activity,
            key=lambda user: user["PasswordLastUsed"],
        )

        print("Most recently active IAM user:")
        print(f"User ID: {most_recent_user['UserId']}")
        print(f"User name: {most_recent_user['UserName']}")
        print(
            f"Password last used: "
            f"{most_recent_user['PasswordLastUsed']}"
        )

    except (BotoCoreError, ClientError) as error:
        print(f"Failed to retrieve IAM users: {error}")
        raise


if __name__ == "__main__":
    get_iam_user_activity()