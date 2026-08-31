#!/usr/bin/env groovy

pipeline {
    agent any

    environment {
        ECR_REPO_NAME = 'python-devops-demo-app'

        EC2_SERVER = 'REPLACE_WITH_EC2_PUBLIC_IP'
        EC2_USER = 'ec2-user'

        SSH_KEY_FILE = credentials('ssh-creds')

        ECR_REGISTRY = 'REPLACE_WITH_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com'

        CONTAINER_PORT = '80'
        HOST_PORT = '8080'

        AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_secret_access_key')
        AWS_DEFAULT_REGION = 'eu-central-1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate Python Environment') {
            steps {
                sh '''
                    python3 --version
                    python3 -c "import boto3, paramiko, requests"
                '''
            }
        }

        stage('Select Image Version') {
            steps {
                script {
                    echo 'Fetching available image versions from ECR...'

                    def result = sh(
                        script: 'python3 exercises/exercise-05-jenkins/get_images.py',
                        returnStdout: true
                    ).trim()

                    if (!result) {
                        error('No ECR image tags were returned.')
                    }

                    def tags = result.split('\\n') as List

                    def selectedVersion = input(
                        message: 'Select image version to deploy',
                        ok: 'Deploy',
                        parameters: [
                            choice(
                                name: 'IMAGE_VERSION',
                                choices: tags,
                                description: 'Choose ECR image version'
                            )
                        ]
                    )

                    env.DOCKER_IMAGE =
                        "${ECR_REGISTRY}/${ECR_REPO_NAME}:${selectedVersion}"

                    echo "Selected image: ${env.DOCKER_IMAGE}"
                }
            }
        }

        stage('Deploy Image') {
            steps {
                echo 'Deploying selected Docker image to EC2...'

                sh '''
                    python3 exercises/exercise-05-jenkins/deploy.py
                '''
            }
        }

        stage('Validate Deployment') {
            steps {
                echo 'Validating deployed application...'

                sh '''
                    python3 exercises/exercise-05-jenkins/validate.py
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment pipeline completed successfully.'
        }

        failure {
            echo 'Deployment pipeline failed. Review the stage logs.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}