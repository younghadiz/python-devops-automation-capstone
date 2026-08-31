# Python DevOps Automation Platform

A production-oriented Python automation project demonstrating practical DevOps workflows across **AWS, Docker, Amazon ECR, Jenkins, Linux, and CI/CD**.

The project automates common cloud operations including AWS resource discovery, IAM activity analysis, EC2 provisioning, application deployment, service monitoring and recovery, ECR image management, and Jenkins-driven deployments to Amazon EC2.

---

## Overview 

Modern DevOps environments require more than infrastructure provisioning. Engineering teams also need automation for operational tasks such as resource discovery, monitoring, recovery, image management, and application deployment.

This project demonstrates how Python can be used alongside AWS and Jenkins to automate those workflows.

The implementation includes five automation areas:

1. AWS subnet discovery
2. IAM user activity analysis
3. Automated EC2 application provisioning and monitoring
4. Amazon ECR repository and image inspection
5. Jenkins-driven application deployment using Python

The project emphasizes modular automation, secure credential handling, deployment validation, and reproducible workflows.

---

## Architecture

```text
                         ┌──────────────────────────┐
                         │      Git Repository      │
                         │    GitHub / GitLab       │
                         └────────────┬─────────────┘
                                      │
                                      │ Source Code
                                      ▼
                         ┌──────────────────────────┐
                         │         Jenkins          │
                         │                          │
                         │  CI/CD Pipeline          │
                         │  Python Automation       │
                         │  Boto3                   │
                         │  Paramiko                │
                         │  Requests                │
                         └───────┬─────────┬────────┘
                                 │         │
                          Boto3  │         │ SSH
                                 │         │
                    ┌────────────▼──┐   ┌──▼──────────────────────┐
                    │  Amazon ECR   │   │   Deployment EC2       │
                    │               │   │                         │
                    │ Image 1.0     │   │ Amazon Linux 2023       │
                    │ Image 2.0     │   │ Docker                  │
                    │ Image 3.0     │   │ Application Container   │
                    └───────────────┘   └─────────────────────────┘


                  Python AWS Automation
                           │
              ┌────────────┼─────────────┐
              │            │             │
              ▼            ▼             ▼
          Amazon VPC      IAM           EC2
          / Subnets      Users       Monitoring
                                        │
                                        ▼
                                Application Health
                                        │
                                Automatic Recovery
```

---

## Technology Stack

| Technology | Purpose                              |
| ---------- | ------------------------------------ |
| Python 3   | Automation and operational scripting |
| Boto3      | AWS SDK for Python                   |
| AWS EC2    | Compute and application hosting      |
| Amazon ECR | Docker image registry                |
| AWS IAM    | Identity and access management       |
| Amazon VPC | Network and subnet discovery         |
| Docker     | Application containerization         |
| Jenkins    | CI/CD orchestration                  |
| Paramiko   | SSH automation from Python           |
| Requests   | HTTP application health validation   |
| Schedule   | Recurring monitoring tasks           |
| Git        | Source control                       |
| GitHub     | Source repository                    |
| GitLab     | Secondary source repository          |

---

## Project Structure

```text
python-devops-automation-capstone/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── Jenkinsfile
│
├── app/
│   ├── Dockerfile
│   └── index.html
│
├── exercises/
│   ├── exercise-01-subnets/
│   │   └── list_subnets.py
│   │
│   ├── exercise-02-iam/
│   │   └── iam_user_activity.py
│   │
│   ├── exercise-03-ec2-monitoring/
│   │   └── ec2_app_monitor.py
│   │
│   ├── exercise-04-ecr/
│   │   └── ecr_images.py
│   │
│   └── exercise-05-jenkins/
│       ├── get_images.py
│       ├── deploy.py
│       └── validate.py
│
├── docs/
    ├── architecture.md
    ├── deployment.md
    ├── security.md
    ├── troubleshooting.md
    └── evidence.md


```

---

## Automation Workflows

### 1. AWS Subnet Discovery

The subnet automation retrieves available AWS subnets using Boto3 and displays their subnet identifiers.

This provides a simple foundation for programmatically discovering AWS networking resources instead of relying on manually configured identifiers.

```text
Python
   │
   ▼
Boto3 EC2 Client
   │
   ▼
AWS VPC
   │
   ▼
Subnets
   │
   ▼
Subnet IDs
```

---

### 2. IAM User Activity Analysis

The IAM automation retrieves AWS IAM users and analyzes their available password activity information.

The workflow:

* retrieves IAM users
* displays user identifiers and names
* reads available `PasswordLastUsed` information
* compares activity timestamps
* identifies the most recently active applicable user

This demonstrates how Python can be used for AWS identity inventory and operational reporting.

---

### 3. EC2 Application Provisioning and Monitoring

The EC2 automation provisions and monitors a Dockerized web application.

The workflow includes:

```text
Python Automation
       │
       ▼
Launch EC2
       │
       ▼
Wait for Instance
       │
       ▼
Configure Server
       │
       ▼
Install Docker
       │
       ▼
Start Application
       │
       ▼
HTTP Health Monitoring
       │
       ├──── Healthy ────► Continue Monitoring
       │
       └──── Repeated Failures
                    │
                    ▼
             Restart Container
```

The monitoring process performs recurring HTTP health checks.

If the application repeatedly fails health validation, the automation attempts to restore service by restarting the application container.

This demonstrates basic automated service recovery and operational monitoring.

---

### 4. Amazon ECR Image Management

The ECR automation discovers repositories and inspects available container images.

The workflow:

```text
Python
   │
   ▼
Boto3 ECR Client
   │
   ▼
Amazon ECR
   │
   ├── Repository Discovery
   │
   └── Image Metadata
            │
            ▼
       Sort by Push Date
            │
            ▼
       Display Image Tags
```

Images are sorted using their push timestamps so the most recently published versions can be identified programmatically.

---

### 5. Jenkins + Python Deployment Pipeline

The final workflow integrates Python automation with Jenkins.

Jenkins retrieves available image versions from Amazon ECR and presents them as a deployment choice.

After an image version is selected, Python performs the remote deployment to the target EC2 instance.

```text
Git Repository
      │
      ▼
   Jenkins
      │
      ▼
Query Amazon ECR
      │
      ▼
Available Image Versions
      │
      ▼
Select Version
      │
      ▼
Generate ECR Authentication
      │
      ▼
SSH to Deployment EC2
      │
      ▼
Docker Login
      │
      ▼
Docker Pull
      │
      ▼
Replace Existing Container
      │
      ▼
Start Selected Release
      │
      ▼
HTTP Validation
```

The pipeline separates AWS discovery, deployment, and validation into dedicated Python scripts.

### Pipeline Stages

```text
Checkout
   ↓
Prepare / Validate Python Environment
   ↓
Select Image Version
   ↓
Deploy Image
   ↓
Validate Deployment
```

The deployment validation script returns a non-zero exit code when the application cannot be validated successfully, allowing Jenkins to correctly mark unsuccessful deployments as failed.

---

## AWS Environment

The project is implemented in:

```text
AWS Region: ca-central-1
```

Separate EC2 instances are used for different automation workflows.

### Automated Monitoring Instance

The monitoring workflow provisions an EC2 instance programmatically for the application monitoring and recovery exercise.

### Deployment Instance

The Jenkins deployment workflow uses a separately prepared Amazon Linux 2023 EC2 instance as its Docker deployment target.

Keeping the deployment target separate from the Jenkins execution environment provides clearer separation between CI/CD orchestration and application runtime responsibilities.

---

## Application Container

The demonstration application is packaged as a Docker image.

Example build:

```bash
docker build -t python-devops-demo-app:1.0 ./app
```

Additional release versions can be created using:

```bash
docker build -t python-devops-demo-app:2.0 ./app
docker build -t python-devops-demo-app:3.0 ./app
```

Images are published to Amazon ECR and subsequently discovered by the Jenkins deployment pipeline.

---

## Python Dependencies

Dependencies are defined in:

```text
requirements.txt
```

```text
boto3
paramiko
requests
schedule
python-dotenv
```

Create an isolated Python environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verify:

```bash
python -c "import boto3, paramiko, requests, schedule; print('Dependencies OK')"
```

---

## Jenkins Configuration

The Jenkins pipeline requires access to AWS and the deployment EC2 server.

The pipeline uses Jenkins Credentials rather than storing secrets directly in source control.

Required credentials include AWS authentication for ECR access and an SSH private key for deployment access.

Example credential identifiers:

```text
jenkins_aws_access_key_id
jenkins_aws_secret_access_key
ssh-creds
```

The SSH credential is configured as:

```text
Kind: SSH Username with private key
Username: ec2-user
ID: ssh-creds
```

Credential values must never be committed to this repository.

---

## IAM Permissions

The Jenkins automation should use a dedicated IAM principal with only the permissions required for the deployment workflow.

Required ECR operations include:

```text
ecr:GetAuthorizationToken
ecr:DescribeImages
ecr:DescribeRepositories
ecr:BatchGetImage
ecr:GetDownloadUrlForLayer
ecr:BatchCheckLayerAvailability
```

Broad administrative permissions are intentionally avoided.

For workloads running directly on AWS, IAM roles and temporary credentials should be preferred over long-lived access keys whenever possible.

---

## Security

Security considerations are incorporated throughout the project.

### Credential Management

The following must never be committed:

```text
AWS access keys
AWS secret access keys
AWS session tokens
SSH private keys
.pem files
.env files containing secrets
Jenkins credentials
ECR authorization tokens
```

Sensitive values should be supplied through:

* Jenkins Credentials
* IAM roles where applicable
* environment variables
* local `.env` files excluded from Git

---

### SSH Access

SSH access to EC2 should be restricted to trusted source addresses.

Avoid:

```text
TCP 22
Source: 0.0.0.0/0
```

Prefer:

```text
TCP 22
Source: TRUSTED_IP/32
```

The Jenkins server should only receive the network access required to perform its deployment responsibilities.

---

### Docker

The deployment container uses a restart policy:

```text
--restart unless-stopped
```

This allows the application container to recover automatically following Docker daemon or server restarts unless it has been intentionally stopped.

---

### ECR Authentication

The deployment automation obtains a current ECR authorization token through Boto3 rather than storing a permanent ECR password in source control.

The token is used for Docker registry authentication before the selected application image is pulled.

---

## Running the Automation

### Subnet Discovery

```bash
python exercises/exercise-01-subnets/list_subnets.py
```

### IAM Activity

```bash
python exercises/exercise-02-iam/iam_user_activity.py
```

### EC2 Monitoring

```bash
python exercises/exercise-03-ec2-monitoring/ec2_app_monitor.py
```

### ECR Image Discovery

```bash
python exercises/exercise-04-ecr/ecr_images.py
```

The Jenkins deployment scripts are intended to execute through the Jenkins pipeline because they depend on pipeline-provided environment variables and credentials.

---

## Deployment Validation

The deployment workflow performs an HTTP request against the deployed application.

Example endpoint:

```text
http://EC2_PUBLIC_IP:8080
```

Successful validation requires an HTTP `200` response.

A failed request or unexpected status causes the Python validation process to exit with a non-zero status, which propagates the failure to Jenkins.

---

## Git Workflow

Development follows a branch-based workflow:

```text
main
  │
  └── develop
        │
        ├── feature/exercise-01-subnets
        ├── feature/exercise-02-iam
        ├── feature/exercise-03-ec2-monitoring
        ├── feature/exercise-04-ecr
        ├── feature/exercise-05-jenkins
        └── feature/project-documentation
```

Feature branches are integrated into `develop` using explicit merge commits.

Example:

```bash
git checkout develop
git merge --no-ff feature/exercise-05-jenkins
```

After validation, `develop` is merged into `main`:

```bash
git checkout main
git merge --no-ff develop
```

This preserves meaningful integration points in the Git history.

---

## Validation

Before merging changes, Python files can be syntax-checked with:

```bash
python -m compileall exercises
```

Dependencies can be verified with:

```bash
python -c "import boto3, paramiko, requests, schedule"
```

Git status should also be reviewed:

```bash
git status
```

Ensure that no secrets, credentials, private keys, temporary files, or local environment files are staged before committing.

---

## Key Engineering Outcomes

This project demonstrates practical experience with:

* Python-based AWS automation
* AWS SDK integration using Boto3
* programmatic infrastructure discovery
* IAM resource inspection
* EC2 provisioning and lifecycle operations
* Docker application deployment
* automated application health monitoring
* basic self-healing workflows
* Amazon ECR repository and image management
* SSH automation with Paramiko
* Jenkins CI/CD integration
* interactive release selection
* automated deployment validation
* least-privilege IAM design
* secure CI/CD credential handling
* Git feature-branch workflows

---

## Repository Security

Before pushing changes, verify:

```bash
git status
```

Review staged files:

```bash
git diff --cached
```

The repository must never contain:

```text
*.pem
AWS credentials
SSH private keys
.env
Jenkins secrets
ECR tokens
passwords
session tokens
```

If a credential is accidentally committed, removing it from the latest file is not sufficient. The credential should be considered compromised, revoked or rotated, and removed from Git history where necessary.

---

## License

This repository is intended for educational, demonstration, and portfolio use.
