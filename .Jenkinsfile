pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr:'20'))
    }
    agent none
    environment {
        STACKIENGBOTTDCREDS = credentials('cbaa2c3c-151e-4ba2-92ed-8f088762467b')
    }
    stages {
        stage('build') {
            steps {
                node(label: 'vagrant_vbox_builder') {
                    sh "mkdir -p ${env.WORKSPACE}/"
                    sh "git clone https://${env.STACKIENGBOTTDCREDS}@github.td.teradata.com/software-manufacturing/stacki-iso-builder.git ${env.WORKSPACE}/stacki-iso-builder-${env.BUILD_NUMBER}"
                    sh "cd ${env.WORKSPACE}/stacki-iso-builder-${env.BUILD_NUMBER} && ./do-build.sh ${env.BUILD_OS} ${env.BUILD_BRANCH}"
                }
            }
        }
    }
}
