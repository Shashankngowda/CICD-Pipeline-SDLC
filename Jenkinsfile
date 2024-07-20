pipeline {
    agent { label 'Jenkins-Agent' }
    
     environment {
        APP_NAME = "django-app"
        RELEASE = "1.0.0"
        DOCKER_USER = "shashank348"
        IMAGE_NAME = "${DOCKER_USER}/${APP_NAME}"
        IMAGE_TAG = "${RELEASE}-${BUILD_NUMBER}"
        DOCKER_REGISTRY_CREDENTIALS = credentials('jenkins-docker-token')
        SONARQUBE_TOKEN = credentials('jenkins-sonarqube-token')
        EC2_SSH_KEY = credentials('Kubernates-ec2-key')
        EC2_USER = "ubuntu"
        EC2_HOST = "172.31.34.177"
    }

    stages {
        stage("Cleanup Workspace") {
            steps {
                cleanWs()
            }
        }

        stage("Checkout from SCM") {
            steps {
                git branch: 'staging', credentialsId: 'github', url: 'https://github.com/Shashankngowda/CICD-Pipeline-SDLC.git'
            }
        }


        stage('SonarQube Code Analysis') {
            steps {
                dir("${WORKSPACE}"){
                // Run SonarQube analysis for Python
                script {
                    def scannerHome = tool name: 'sonarqube-scanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withSonarQubeEnv('sonarqube-server') {
                        sh "${scannerHome}/bin/sonar-scanner \
                            -D sonar.projectVersion=1.0-SNAPSHOT \
                            -D sonar.qualityProfile=Python-Quality-Profile \
                            -D sonar.projectBaseDir=${WORKSPACE} \
                            -D sonar.projectKey=sample-app \
                            -D sonar.sourceEncoding=UTF-8 \
                            -D sonar.language=python \
                            -D sonar.host.url=http://172.31.6.143:9000"
                    }
                }
            }
            }
       }

        stage("Quality Gate"){
           steps {
               script {
                    waitForQualityGate abortPipeline: false, credentialsId: 'jenkins-sonarqube-token'
                }	
            }

        }

        stage("Build Docker Image") {
            steps {
                script {
                        docker_image = docker.build "${IMAGE_NAME}"
                }
                }
        }
        
        stage("Push Docker Image") {
            steps {
                script {
                    docker.withRegistry('https://registry-1.docker.io/v1/', 'jenkins-docker-token') {
                        docker_image.push("${IMAGE_TAG}")
                        docker_image.push('latest')
                    }
                }
            }
        }



        stage("Trivy Scan") {
           steps {
               script {
	            sh ('docker run -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image shashank348/django-app:latest --no-progress --scanners vuln  --exit-code 0 --severity HIGH,CRITICAL --format table')
               }
           }
       }

        stage("Cleanup Docker Images") {
            steps {
                script {
                   
                    sh "docker rmi ${IMAGE_NAME}"

                    
                }
            }
        }

        stage("Deploy to EC2") {
            steps {
                script {
                    sshagent(['jenkins-ec2-key']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << EOF
                            echo ${DOCKER_REGISTRY_CREDENTIALS} | docker login -u ${DOCKER_USER} --password-stdin
                            docker pull ${IMAGE_NAME}:latest
                            docker stop my-app || true
                            docker rm my-app || true
                            docker run -d --name my-app -p 80:80 ${IMAGE_NAME}:latest
                            EOF
                        """
                    }
                }
            }
        }
    }

    post {
        failure {
            emailext body: '''${SCRIPT, template="groovy-html.template"}''', 
                     subject: "${env.JOB_NAME} - Build # ${env.BUILD_NUMBER} - Failed", 
                     mimeType: 'text/html', to: "shashankhn7878@gmail.com"
        }
        success {
            emailext body: '''${SCRIPT, template="groovy-html.template"}''', 
                     subject: "${env.JOB_NAME} - Build # ${env.BUILD_NUMBER} - Successful", 
                     mimeType: 'text/html', to: "shashankhn7878@gmail.com"
        }      
    }
}
