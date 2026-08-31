# Architecture

The project demonstrates Python-based automation across AWS and CI/CD.

## Core Components

- Python/Boto3 for AWS API automation
- AWS EC2 for compute
- IAM for user activity inspection
- Amazon ECR for Docker image storage
- Jenkins for deployment orchestration
- Paramiko for SSH-based remote operations
- Requests for HTTP validation
- Schedule for recurring health checks

## Deployment Flow

Developer
→ GitHub/GitLab
→ Jenkins
→ Python
→ Amazon ECR
→ EC2
→ HTTP validation

## Monitoring Flow

Python scheduler
→ HTTP request
→ Nginx
→ count consecutive failures
→ restart container after five failures