pipeline {
  agent any

  stages {
    stage('Backend checks') {
      steps {
        sh 'python -m pip install -r backend/requirements.txt'
        sh 'PYTHONPATH=backend python -m compileall backend/app'
      }
    }

    stage('Frontend build') {
      steps {
        dir('frontend') {
          sh 'npm ci'
          sh 'npm run build'
        }
      }
    }
  }
}
