pipeline {
  agent any
  options { timestamps() }
  environment {
    REGISTRY = 'localhost:5051'
    IMAGE    = 'grocery-app'
  }
  stages {
    stage('Checkout') {
      steps { git branch: 'main', url: 'https://github.com/Tejas75060/grocery_devops.git' }
    }
    stage('Build & Test') {
      // Run in python:3.11 (matches the app image) sharing the Jenkins
      // workspace via --volumes-from so dependency wheels resolve cleanly.
      steps {
        sh 'docker run --rm --volumes-from jenkins -w "$WORKSPACE" python:3.11-slim bash -c "pip install -q -U pip && pip install -q -r app/requirements.txt && pytest -q --junitxml=reports/junit.xml"'
      }
      post { always { junit allowEmptyResults: true, testResults: 'reports/junit.xml' } }
    }
    stage('Docker Build') {
      steps { sh 'docker build -t $REGISTRY/$IMAGE:$BUILD_NUMBER -t $REGISTRY/$IMAGE:latest .' }
    }
    stage('Push to Registry') {
      steps { sh 'docker push $REGISTRY/$IMAGE:$BUILD_NUMBER && docker push $REGISTRY/$IMAGE:latest' }
    }
    stage('Deploy') {
      steps { echo 'Deploy: kubectl set image deployment/grocery-app on the kind cluster (requires a kubeconfig credential — see the repo Jenkinsfile).' }
    }
  }
}
