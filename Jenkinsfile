
pipeline {
  agent any
  environment {
  DOCKERHUB_CREDENTIALS = 'dockerhub-creds' // set this credential in Jenkins (username/password)
  DOCKERHUB_REPO = 'bhargavk055/devops-assignment' // Docker Hub repo (username/repo)
    IMAGE_TAG = "${env.BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Agent Diagnostics') {
      steps {
        script {
          // Print which shells and docker are available on the agent to help debugging
          try {
            sh 'echo "-- POSIX shell detected --"; command -v sh || command -v bash || true; sh -c "echo sh OK; uname -a || true" || true'
          } catch (err) {
            echo "POSIX shell not available or sh failed: ${err}"
          }

          // Windows fallback check
          try {
            bat 'echo -- Windows shell detected -- & where sh || where bash || echo no-posix-shell & docker --version'
          } catch (err) {
            echo "Windows shell checks failed or docker missing: ${err}"
          }
        }
      }
    }

    stage('Build Image') {
      steps {
        script {
          // Try POSIX shell first; fall back to Windows bat if sh isn't available
          try {
            sh "docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} ./web"
          } catch (err) {
            echo "sh failed or isn't available, falling back to bat: ${err}"
            bat "docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} ./web"
          }
        }
      }
    }

    stage('Smoke Test') {
      steps {
        script {
          // Run the smoke test; prefer sh but fall back to bat when sh is not present
          try {
            sh 'docker network create jenkins-test-net || true'
            sh 'docker run -d --name jenkins-test-db --network jenkins-test-net -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=appdb -e MYSQL_USER=appuser -e MYSQL_PASSWORD=apppassword mysql:8.0'
            sh 'sleep 10'
            sh "docker run -d --name jenkins-test-app --network jenkins-test-net -e DB_HOST=jenkins-test-db -e DB_USER=appuser -e DB_PASSWORD=apppassword -e DB_NAME=appdb ${DOCKERHUB_REPO}:${IMAGE_TAG} || true"
            sh 'sleep 5'
            sh 'docker run --network jenkins-test-net --rm curlimages/curl:8.2.1 -sSf http://jenkins-test-app:5000 || true'
            sh 'docker rm -f jenkins-test-app jenkins-test-db || true'
            sh 'docker network rm jenkins-test-net || true'
          } catch (err) {
            echo "POSIX shell steps failed or not available, using Windows bat fallback: ${err}"
            bat 'docker network create jenkins-test-net || exit 0'
            bat 'docker run -d --name jenkins-test-db --network jenkins-test-net -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=appdb -e MYSQL_USER=appuser -e MYSQL_PASSWORD=apppassword mysql:8.0'
            bat 'timeout /t 10 /nobreak >nul'
            bat "docker run -d --name jenkins-test-app --network jenkins-test-net -e DB_HOST=jenkins-test-db -e DB_USER=appuser -e DB_PASSWORD=apppassword -e DB_NAME=appdb ${DOCKERHUB_REPO}:${IMAGE_TAG} || exit 0"
            bat 'timeout /t 5 /nobreak >nul'
            bat 'docker run --network jenkins-test-net --rm curlimages/curl:8.2.1 -sSf http://jenkins-test-app:5000 || exit 0'
            bat 'docker rm -f jenkins-test-app jenkins-test-db || exit 0'
            bat 'docker network rm jenkins-test-net || exit 0'
          }
        }
      }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          script {
            // Try docker login/push with sh first, fall back to bat if needed
            try {
              sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
              sh 'docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}'
            } catch (err) {
              echo "sh login/push failed or not available, falling back to Windows bat: ${err}"
              // Windows: use PowerShell to read password from environment and pipe to docker login
              bat 'powershell -Command "[Console]::OpenStandardOutput() | Out-Null; $env:DOCKER_PASS | docker login -u %DOCKER_USER% --password-stdin"'
              bat "docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}"
            }
          }
        }
      }
    }
  }
}

