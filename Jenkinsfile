
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

    stage('Build Image') {
      steps {
        script {
          sh 'docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} ./web'
        }
      }
    }

    stage('Smoke Test') {
      steps {
        script {
          // Start a temporary DB and the built image to run a quick health check
          sh 'docker network create jenkins-test-net || true'
          sh 'docker run -d --name jenkins-test-db --network jenkins-test-net -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=appdb -e MYSQL_USER=appuser -e MYSQL_PASSWORD=apppassword mysql:8.0'
          sh 'sleep 10'
          sh 'docker run -d --name jenkins-test-app --network jenkins-test-net -e DB_HOST=jenkins-test-db -e DB_USER=appuser -e DB_PASSWORD=apppassword -e DB_NAME=appdb ${DOCKERHUB_REPO}:${IMAGE_TAG} || true'
          // simple check: curl the app endpoint
          sh 'sleep 5'
          sh 'docker run --network jenkins-test-net --rm curlimages/curl:8.2.1 -sSf http://jenkins-test-app:5000 || true'
          // cleanup
          sh 'docker rm -f jenkins-test-app jenkins-test-db || true'
          sh 'docker network rm jenkins-test-net || true'
        }
      }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
          sh 'docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}'
        }
      }
    }
  }
}

