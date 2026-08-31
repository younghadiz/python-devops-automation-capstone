import os
import sys
import time

import requests


server = os.environ["EC2_SERVER"]
host_port = os.environ["HOST_PORT"]

url = f"http://{server}:{host_port}"

print("Waiting for the application to start...")
time.sleep(15)

try:
    response = requests.get(
        url,
        timeout=10,
    )

    if response.status_code == 200:
        print(
            f"Application is running successfully: "
            f"{url}"
        )
        sys.exit(0)

    print(
        f"Application deployment validation failed. "
        f"HTTP status: {response.status_code}"
    )

    sys.exit(1)

except requests.RequestException as error:
    print(
        f"Application is not accessible: {error}"
    )
    sys.exit(1)