pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                script {
                    git 'https://github.com/hafeezabhanu9/stress_test.git'
                }
            }
        }
        stage('Run Stress Test') {
            steps {
                script {
                    sh 'python3 stress_data.py'
                }
            }
        }
    }
    post {
        success {
            echo 'Stress test completed successfully!'
        }
        failure {
            echo 'Stress test failed.' //failed
        }
    }
}

