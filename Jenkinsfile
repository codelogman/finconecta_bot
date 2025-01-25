pipeline {
    agent any  

    environment {
        IMAGE_NAME = 'codelogman/finconecta_bot'
        IMAGE_TAG = 'latest'
        REGISTRY = 'docker.io'
        KUBE_CONFIG_PATH = '/finconecta/kubeconfig'  
    }

    stages {
        stage('Build') {
            steps {
                script {
                    // Construir la imagen de Docker
                    echo "Building Docker image..."
                    sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Test') {
            steps {
                script {                    
                    echo "Running tests..."
                    sh 'pytest tests/'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "Pushing Docker image to Docker Hub..."
                    withCredentials([usernamePassword(credentialsId: '_docker-hub-credentials_', usernameVariable: '__DOCKER_USER__', passwordVariable: '__PASS__')]) {
                        sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                        sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "Deploying to Kubernetes..."
                    sh """
                    kubectl --kubeconfig=${KUBE_CONFIG_PATH} apply -f deployment.yaml
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }

        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed!'
        }
    }
}

