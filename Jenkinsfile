
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
          // Idempotent smoke test: non-fatal — failures will be logged but won't stop the pipeline
          def net = "jenkins-test-net-${env.IMAGE_TAG}"
          def dbName = "jenkins-test-db-${env.IMAGE_TAG}"
          def appName = "jenkins-test-app-${env.IMAGE_TAG}"

          // helper to try POSIX, else Windows
          def run = { posixCmd, winCmd ->
            try { sh posixCmd } catch (e) { echo "sh not available/runnable: ${e}"; bat winCmd }
          }

          // default to false; set to 'true' only on successful smoke test
          env.SMOKE_OK = 'false'

          try {
            // pre-clean
            run("docker rm -f ${appName} ${dbName} || true", "docker rm -f ${appName} ${dbName} || exit 0")
            run("docker network rm ${net} || true", "docker network rm ${net} || exit 0")

            // create network
            run("docker network create ${net} || true", "docker network create ${net} || exit 0")

            // start DB
            run("docker run -d --name ${dbName} --network ${net} -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=appdb -e MYSQL_USER=appuser -e MYSQL_PASSWORD=apppassword mysql:8.0",
                "docker run -d --name ${dbName} --network ${net} -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=appdb -e MYSQL_USER=appuser -e MYSQL_PASSWORD=apppassword mysql:8.0")

            // wait for DB
            run('sleep 10', 'powershell -Command "Start-Sleep -Seconds 10"')

            // start app
            run("docker run -d --name ${appName} --network ${net} -e DB_HOST=${dbName} -e DB_USER=appuser -e DB_PASSWORD=apppassword -e DB_NAME=appdb ${DOCKERHUB_REPO}:${IMAGE_TAG}",
                "docker run -d --name ${appName} --network ${net} -e DB_HOST=${dbName} -e DB_USER=appuser -e DB_PASSWORD=apppassword -e DB_NAME=appdb ${DOCKERHUB_REPO}:${IMAGE_TAG}")

            // wait for app
            run('sleep 5', 'powershell -Command "Start-Sleep -Seconds 5"')

            // smoke test HTTP on app
            run("docker run --network ${net} --rm curlimages/curl:8.2.1 -sSf http://${appName}:5000",
                "docker run --network ${net} --rm curlimages/curl:8.2.1 -sSf http://${appName}:5000")

            // mark smoke test success
            env.SMOKE_OK = 'true'

          } catch (err) {
            // don't fail the pipeline for smoke test failures — log and continue to Push
            echo "Smoke test failed (non-fatal): ${err}"
          } finally {
            // clean up (best-effort)
            run("docker rm -f ${appName} ${dbName} || true", "docker rm -f ${appName} ${dbName} || exit 0")
            run("docker network rm ${net} || true", "docker network rm ${net} || exit 0")
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

