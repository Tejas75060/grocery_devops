// Jenkins declarative pipeline for the Grocery Delivery Platform.
// Generic / self-hosted — no cloud-specific steps. Works with any Docker
// registry (Docker Hub, Harbor, GitLab, a local registry:2, etc.).
pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timeout(time: 30, unit: 'MINUTES')
  }

  environment {
    // Override these in the Jenkins job / folder env or as global props.
    REGISTRY        = "${env.REGISTRY ?: 'localhost:5000'}"
    IMAGE_NAME      = "${env.IMAGE_NAME ?: 'grocery-app'}"
    IMAGE_TAG       = "${env.GIT_COMMIT?.take(7) ?: env.BUILD_NUMBER}"
    IMAGE           = "${REGISTRY}/${IMAGE_NAME}"
    // Jenkins "Username with password" credential id for the registry.
    REGISTRY_CREDS  = 'registry-credentials'
    // kubeconfig file credential for the deploy stage.
    KUBECONFIG_CRED = 'kubeconfig'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git rev-parse --short HEAD > .gitsha && cat .gitsha'
      }
    }

    stage('Build') {
      steps {
        // Install deps in an ephemeral venv to validate the build.
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -U pip
          pip install -r app/requirements.txt
        '''
      }
    }

    stage('Test') {
      steps {
        sh '''
          . .venv/bin/activate
          pytest -q --junitxml=reports/junit.xml
        '''
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'reports/junit.xml'
        }
      }
    }

    stage('Docker Build') {
      steps {
        sh '''
          docker build -t ${IMAGE}:${IMAGE_TAG} -t ${IMAGE}:latest .
        '''
      }
    }

    stage('Push to Registry') {
      steps {
        withCredentials([usernamePassword(
            credentialsId: "${REGISTRY_CREDS}",
            usernameVariable: 'REG_USER',
            passwordVariable: 'REG_PASS')]) {
          sh '''
            echo "$REG_PASS" | docker login ${REGISTRY} -u "$REG_USER" --password-stdin
            docker push ${IMAGE}:${IMAGE_TAG}
            docker push ${IMAGE}:latest
            docker logout ${REGISTRY}
          '''
        }
      }
    }

    stage('Deploy') {
      steps {
        // Roll the new image onto the local kind/minikube cluster.
        withCredentials([file(
            credentialsId: "${KUBECONFIG_CRED}",
            variable: 'KUBECONFIG')]) {
          sh '''
            kubectl -n grocery set image deployment/grocery-app \
              grocery-app=${IMAGE}:${IMAGE_TAG} --record
            kubectl -n grocery rollout status deployment/grocery-app --timeout=120s
          '''
        }
      }
    }
  }

  post {
    success { echo "Deployed ${IMAGE}:${IMAGE_TAG} successfully." }
    failure { echo "Pipeline failed — see stage logs above." }
    always  { sh 'docker image prune -f || true' }
  }
}
