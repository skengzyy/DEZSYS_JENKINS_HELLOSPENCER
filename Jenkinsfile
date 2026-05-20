pipeline {
    agent any

    stages {
        stage('Source') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }
        stage('Build') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t hellospencer:latest .'
            }
        }
        stage('Test') {
            steps {
                echo 'Running unit tests...'
                sh 'docker run --rm hellospencer:latest python -m pytest tests/ -v'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
                sh '''
                  docker stop hellospencer-app 2>/dev/null || true
                  docker rm hellospencer-app 2>/dev/null || true
                  docker run -d --name hellospencer-app -p 5001:5000 hellospencer:latest
                '''
            }
        }
    }
    post {
        success { echo 'Pipeline erfolgreich!' }
        failure { echo 'Pipeline fehlgeschlagen!' }
    }
}
