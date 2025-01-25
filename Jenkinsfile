pipeline {
    agent any  # Define que Jenkins puede ejecutarlo en cualquier agente disponible

    environment {
        IMAGE_NAME = 'codelogman/finconecta_bot'
        IMAGE_TAG = 'latest'
        REGISTRY = 'docker.io'
        KUBE_CONFIG_PATH = '/path/to/kubeconfig'  # Ruta al archivo kubeconfig para Kubernetes
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
                    // Aquí puedes agregar tus pruebas unitarias o de integración
                    echo "Running tests..."
                    // Puedes usar pytest o cualquier framework de pruebas que estés utilizando
                    sh 'pytest tests/'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Iniciar sesión en Docker Hub
                    echo "Pushing Docker image to Docker Hub..."
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                        sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Desplegar en Kubernetes
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
            cleanWs()  // Limpiar el espacio de trabajo después de cada ejecución
        }

        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed!'
        }
    }
}

