pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr:'20'))
    }
    agent none
    stages {
        stage('build') {
            steps {
                node(label: 'vagrant_vbox_builder') {
                    sh "hostname"
                    sh "whoami"
                    sh "mkdir -p ${env.WORKSPACE}/stacki-iso-builder-${env.BUILD_NUMBER}"
                    sh "tar -xvzf /export/stacki-iso-builder.tar.gz -C ${env.WORKSPACE}/stacki-iso-builder-${env.BUILD_NUMBER} --strip-components 1"
                    sh "cd ${env.WORKSPACE}/stacki-iso-builder-${env.BUILD_NUMBER} && ./do-build.sh ${env.BUILD_OS} ${env.BUILD_BRANCH}"
                }
            }
        }
    }
    post {
        always {
            node(label: 'vagrant_vbox_builder') {
                sh "cd ${env.WORKSPACE}/stacki-iso-builder-${env.BUILD_NUMBER} && vagrant destroy -f"
            }
        }
    }
}
