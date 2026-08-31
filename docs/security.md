# Security Practices

## Secrets

Never commit:

- AWS access keys
- AWS secret keys
- `.env`
- SSH private keys
- EC2 `.pem` files
- Jenkins credentials
- ECR authorization tokens
- GitHub tokens
- GitLab tokens

## AWS

Use dedicated IAM identities and least privilege.

For production AWS-hosted automation, prefer IAM roles over static access keys.

## SSH

Restrict port 22 to an administrator IP `/32`.

Do not configure:

`0.0.0.0/0`

for SSH.

## Jenkins

Store credentials in Jenkins Credentials, not the Jenkinsfile.

Do not print secrets to pipeline output.

## Screenshots

Blur or crop:

- AWS Account IDs where unnecessary
- IAM user IDs
- private IP information where sensitive
- credentials
- tokens
- private keys
- email addresses if personal