pipeline {
    agent { label 'Jenkins-Agent' }
    
    environment {
        DOCKER_IMAGE = "shashank/django-app"
        IMAGE_TAG = "latest"
        DOCKER_REGISTRY_CREDENTIALS = 'docker-credentials'
        SONARQUBE_SERVER = 'http://13.232.52.157:9000'  // Update with your SonarQube server URL
        SONARQUBE_TOKEN = credentials('sonarqube-token')   // Update with your SonarQube server URL
    }
    
    stages {
        stage("Cleanup Workspace") {
            steps {
                cleanWs()
            }
        }

        stage("Checkout from SCM") {
            steps {
                git branch: 'main', credentialsId: 'github', url: 'https://github.com/Shashankngowda/CICD-Pipeline-SDLC.git'
            }
        }

        stage("Build Docker Image") {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
                }
            }
        }

        stage("Static Code Analysis") {
            steps {
                // Assuming you have Flake8 or other static analysis tools for Python installed
                sh "flake8 ."  // Example command for static code analysis
            }
        }

        stage("SonarQube Analysis") {
            steps {
                script {
                    withSonarQubeEnv('SonarQube') {
                        // Execute SonarScanner for Python
                        sh """
                        sonar-scanner \
                            -Dsonar.projectKey=django-project-key \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONARQUBE_SERVER} \
                            -Dsonar.login=${env.SONARQUBE_TOKEN}
                        """
                    }
                }
            }
        }

        stage("Quality Gate") {
            steps {
                script {
                    timeout(time: 1, unit: 'HOURS') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage("Push Docker Image") {
            steps {
                script {
                    docker.withRegistry('', DOCKER_REGISTRY_CREDENTIALS) {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push('latest')
                    }
                }
            }
        }

        stage("Trivy Scan") {
            steps {
                script {
                    sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ${DOCKER_IMAGE}:${IMAGE_TAG} --no-progress --scanners vuln --exit-code 0 --severity HIGH,CRITICAL --format table"
                }
            }
        }

        stage("Cleanup Docker Images") {
            steps {
                script {
                    sh "docker rmi ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    sh "docker rmi ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage("Trigger CD Pipeline") {
            steps {
                script {
                    sh "curl -v -k --user clouduser:${JENKINS_API_TOKEN} -X POST -H 'cache-control: no-cache' -H 'content-type: application/x-www-form-urlencoded' --data 'IMAGE_TAG=${IMAGE_TAG}' 'ec2-13-232-128-192.ap-south-1.compute.amazonaws.com:8080/job/gitops-register-app-cd/buildWithParameters?token=gitops-token'"
                }
            }
        }
    }

    post {
        failure {
            emailext body: '''${SCRIPT, template="groovy-html.template"}''', 
                     subject: "${env.JOB_NAME} - Build # ${env.BUILD_NUMBER} - Failed", 
                     mimeType: 'text/html', to: "shashankhn7788@gmail.com"
        }
        success {
            emailext body: '''${SCRIPT, template="groovy-html.template"}''', 
                     subject: "${env.JOB_NAME} - Build # ${env.BUILD_NUMBER} - Successful", 
                     mimeType: 'text/html', to: "shashankhn7788@gmail.com"
        }      
    }
}
