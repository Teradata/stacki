pipeline {
    agent {
        label 'vagrant_kvm_builder'
    }

    environment {
        TD_GITHUB = credentials('cbaa2c3c-151e-4ba2-92ed-8f088762467b')
        GITHUB = credentials('88f234ac-6b93-4c41-92d2-1329c97e2254')
        ARTIFACTORY = credentials('d1a4e414-0526-4973-bea5-9d219d884f03')
        GITHUB_TOKEN = credentials('72702790-6cee-470b-94d0-1c3eb246a71d')
        BLACKDUCK_TOKEN = credentials('cb9c5430-f974-46e3-9d25-baeab4873db9')
        ESXI_PASS = credentials('8af95130-9b78-4e7a-9d3a-bec7ab54716b')
        JENKINS = credentials('8b24c6e2-8589-4feb-afc2-3d0175854b11')

        PIPELINE = env.JOB_NAME.split('/')[0].trim()
        PLATFORM = env.PIPELINE.split('-')[-1].trim()
        NORMALIZED_BRANCH = env.BRANCH_NAME.replaceAll('[/-]', '_')

        ART_URL = "https://sdartifact.td.teradata.com/artifactory"
        ART_ISO_PATH = "software-manufacturing/pallets/stacki"
        ART_QCOW_PATH = "software-manufacturing/kvm-images/stacki"
        ART_OVA_PATH = "software-manufacturing/ova-images/stacki"
        ART_VBOX_PATH = "software-manufacturing/vbox-images/stacki"
    }

    options {
        ansiColor('xterm')
        buildDiscarder(logRotator(daysToKeepStr: env.BRANCH_NAME == 'master' ? '365' : '20'))
        skipDefaultCheckout()
        timestamps()
    }

    triggers {
        // Nightly build of develop (at 3am)
        cron(env.BRANCH_NAME == 'develop' ? 'TZ=America/Los_Angeles\n0 3 * * *' : '')
    }

    stages {
        stage('Source') {
            steps {
                // Update the Stacki Builds website
                build job: 'rebuild_stacki-builds_website', wait: false

                // Get the souce code we're going to build
                // Note: github.com checkout is flaky, so we disable the default checkout
                // and do it here with retries.
                dir('stacki') {
                    retry(3) {
                        script {
                            // Note: There is a bug in Jenkins where a timeout causes the job to
                            // abort unless you catch the FlowInterruptedException.
                            // https://issues.jenkins-ci.org/browse/JENKINS-51454
                            timeout(15) {
                                try {
                                    // Note: there is currently a bug in scm checkout where it doesn't
                                    // set environment variables, we we do by hand in a script
                                    checkout(scm).each { k,v -> env.setProperty(k, v) }

                                    // Remove the git reference because it breaks stack-releasenotes
                                    sh('git repack -a -d')
                                    sh('rm -f .git/objects/info/alternates')

                                    // Add the last git log subject as the description in the GUI
                                    currentBuild.description = sh(
                                        returnStdout: true,
                                        script: 'git log -1 --pretty=format:%s'
                                    )
                                }
                                catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                                    error 'Source checkout timed out'
                                }
                            }
                        }
                    }
                }

                // Get the repository testing scripts
                sh 'git clone https://${TD_GITHUB}@github.td.teradata.com/software-manufacturing/stacki-git-tests.git'
            }
        }

        stage('Check Branch') {
            // Only need these checks on one platform for feature and bugfix branches
            when {
                environment name: 'PLATFORM', value: 'sles15'
                anyOf {
                    branch 'feature/*'
                    branch 'bugfix/*'
                }
            }

            parallel {
                stage('Number Of Commits') {
                    steps {
                        dir('stacki') {
                            script {
                                // Check the number of commits on the branch
                                def status = sh(
                                    returnStatus: true,
                                    script: "python3 ../stacki-git-tests/verify-branch-base.py"
                                )

                                // Report the status to github.com
                                if (status == 0) {
                                    githubNotify(
                                        context: 'Check: Branch commits',
                                        status: 'SUCCESS',
                                        description: 'ready to merge'
                                    )
                                }
                                else {
                                    githubNotify(
                                        context: 'Check: Branch commits',
                                        status: 'FAILURE',
                                        description: 'not ready to merge'
                                    )
                                }
                            }
                        }
                    }
                }

                stage('Commit Message') {
                    steps {
                        dir('stacki') {
                            script {
                                // Check the commit message formatting
                                def status = sh(
                                    returnStatus: true,
                                    script: 'python3 ../stacki-git-tests/validate-commit-message.py'
                                )

                                // Report the status to github.com
                                if (status == 0) {
                                    githubNotify(
                                        context: 'Check: Commit message',
                                        status: 'SUCCESS',
                                        description: 'ready to merge'
                                    )
                                }
                                else {
                                    githubNotify(
                                        context: 'Check: Commit message',
                                        status: 'FAILURE',
                                        description: 'not ready to merge'
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Build') {
            environment {
                ISOS = '../../..'
                PYPI_CACHE = 'true'
            }

            steps {
                // Figure out if we are a release build
                script {
                    if (env.TAG_NAME ==~ /stacki-.*/ && env.BRANCH_NAME == env.TAG_NAME) {
                        env.IS_RELEASE = 'true'
                    }
                    else {
                        env.IS_RELEASE = 'false'
                    }
                }

                // Get some ISOs we'll need for build
                script {
                    switch(env.PLATFORM) {
                        case 'redhat7':
                            sh 'cp /export/www/installer-isos/CentOS-7-x86_64-Everything-1810.iso .'
                            // sh 'cp /export/www/stacki-isos/redhat7/os/os-7.6_20191101-redhat7.x86_64.disk1.iso .'
                            // env.OS_PALLET = 'os-7.6_20191101-redhat7.x86_64.disk1.iso'
                            break

                        case 'sles15':
                            sh 'cp /export/www/installer-isos/SLE-15-SP1-Installer-DVD-x86_64-GM-DVD1.iso .'
                            sh 'cp /export/www/installer-isos/SLE-15-SP1-Packages-x86_64-GM-DVD1.iso .'
                            break

                        case 'sles12':
                            sh 'cp /export/www/installer-isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso .'
                            sh 'cp /export/www/installer-isos/SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso .'
                            break

                        case 'sles11':
                            sh 'cp /export/www/installer-isos/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso .'
                            sh 'cp /export/www/installer-isos/SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso .'
                            break
                    }
                }

                // Build our ISO
                dir('stacki/tools/iso-builder') {
                    // Give the build up to 60 minutes to finish
                    timeout(60) {
                        script {
                            try {
                                sh 'vagrant up'
                            }
                            catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                                error 'Build timed out'
                            }
                        }
                    }
                }

                // Move the ISO into the root of the workspace, renaming it for TSS if needed
                script {
                    sh 'mv stacki/stacki-*.iso ./'

                    switch(env.PLATFORM) {
                        case 'sles15':
                            sh 'mv $(ls ./stacki-*.iso) $(ls ./stacki-*.iso | sed -e "s|stacki-|stacki-15.1-|")'
                            break
                        case 'sles12':
                            sh 'mv $(ls ./stacki-*.iso) $(ls ./stacki-*.iso | sed -e "s|stacki-|stacki-12.3-|")'
                            break
                        case 'sles11':
                            sh 'mv $(ls ./stacki-*.iso) $(ls ./stacki-*.iso | sed -e "s|stacki-|stacki-11.3-|")'
                            break
                        case 'redhat7':
                            // Note: For now, we no longer build StackiOS
                            // sh 'mv stacki/stackios-*.iso ./'
                            break
                    }
                }

                // Set an environment variable with the ISO filename
                script {
                    env.ISO_FILENAME = findFiles(glob: 'stacki-*.iso')[0].name
                }

                // Fingerprint the file, which Jenkins or our pipeline might use some day
                fingerprint "${env.ISO_FILENAME}"

                // If we are Redhat, fingerprint the StackiOS ISO as well
                // script {
                //     if (env.PLATFORM == 'redhat7') {
                //         env.STACKIOS_FILENAME = findFiles(glob: 'stackios-*.iso')[0].name
                //         fingerprint "${env.STACKIOS_FILENAME}"
                //     }
                // }
            }

            post {
                always {
                    // Update the Stacki Builds website
                    build job: 'rebuild_stacki-builds_website', wait: false

                    // Remove the pallet builder VM
                    dir('stacki/tools/iso-builder') {
                        sh 'vagrant destroy -f || true'
                    }
                }

                success {
                    // Tell github.com this commit built
                    githubNotify(
                        context: "Build: ${env.PLATFORM}",
                        description: "build succeeded",
                        status: 'SUCCESS'
                    )
                }

                failure {
                    // Tell github.com this commit failed to build
                    githubNotify(
                        context: "Build: ${env.PLATFORM}",
                        description: "build failed",
                        status: 'FAILURE'
                    )

                    // And the Slack #stacki-bot channel
                    slackSend(
                        channel: '#stacki-builds',
                        color: 'danger',
                        message: """\
                            Stacki build has failed.
                            *Branch:* ${env.GIT_BRANCH}
                            *OS:* ${env.PLATFORM}
                            <${env.RUN_DISPLAY_URL}|View the pipeline job>
                        """.stripIndent(),
                        tokenCredentialId: 'slack-token-stacki'
                    )
                }
            }
        }

        stage('Upload') {
            parallel {
                stage('Artifactory') {
                    steps {
                        // Setup Artifactory access
                        rtServer(
                            id: "td-artifactory",
                            url: "${env.ART_URL}",
                            credentialsId: "d1a4e414-0526-4973-bea5-9d219d884f03",
                            timeout: 3600
                        )

                        // Figure out our Artifactory OS
                        script {
                            env.ART_OS = [
                                'sles11': 'sles-11.3',
                                'sles12': 'sles-12.3',
                                'sles15': 'sles-15.1',
                                'redhat7': 'redhat-7.4'
                            ][env.PLATFORM]
                        }

                        // Upload the Stacki ISO to artifactory snapshot
                        rtUpload(
                            serverId: "td-artifactory",
                            spec: """
                                {
                                    "files": [{
                                        "pattern": "${env.ISO_FILENAME}",
                                        "target": "pkgs-external-snapshot-sd/${env.ART_ISO_PATH}/${env.ART_OS}/${env.GIT_BRANCH}/"
                                    }]
                                }
                            """
                        )
                    }

                    post {
                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki failed to upload to Artifactory.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }
                    }
                }

                stage('Stacki Builds') {
                    steps {
                        // Create our MD5 of the ISO
                        sh 'md5sum $ISO_FILENAME > $ISO_FILENAME.md5'

                        // Make sure our web directory exists
                        sh 'mkdir -p /export/www/stacki-isos/$PLATFORM/stacki/$NORMALIZED_BRANCH'

                        // Copy the files over
                        sh 'cp $ISO_FILENAME /export/www/stacki-isos/$PLATFORM/stacki/$NORMALIZED_BRANCH/'
                        sh 'cp $ISO_FILENAME.md5 /export/www/stacki-isos/$PLATFORM/stacki/$NORMALIZED_BRANCH/'

                        // Note: For now, we no longer build StackiOS
                        // If we are Redhat, we should have a StackiOS ISO as well
                        // script {
                        //     if (env.PLATFORM == 'redhat7') {
                        //         // Create our MD5 of the ISO
                        //         sh 'md5sum $STACKIOS_FILENAME > $STACKIOS_FILENAME.md5'

                        //         // Make sure our web directory exists
                        //         sh 'mkdir -p /export/www/stacki-isos/redhat7/stackios/$NORMALIZED_BRANCH'

                        //         // Copy the files over
                        //         sh 'cp $STACKIOS_FILENAME /export/www/stacki-isos/redhat7/stackios/$NORMALIZED_BRANCH/'
                        //         sh 'cp $STACKIOS_FILENAME.md5 /export/www/stacki-isos/redhat7/stackios/$NORMALIZED_BRANCH/'
                        //     }
                        // }
                    }

                    post {
                        failure {
                            // Notify the Slack #stacki-builds channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki failed to copy to Stacki Builds website.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }
                    }
                }
            }
        }

        stage('Setup Tests') {
            steps {
                // Build the test-framework
                dir('stacki/test-framework') {
                    sh 'make'
                }

                // Pre-cache the installer ISOs
                dir('stacki/test-framework/.cache') {
                    script {
                        switch(env.PLATFORM) {
                            case 'redhat7':
                                sh 'cp /export/www/installer-isos/CentOS-7-x86_64-Everything-1810.iso .'
                                break

                            case 'sles15':
                                sh 'cp /export/www/installer-isos/SLE-15-SP1-Installer-DVD-x86_64-GM-DVD1.iso .'
                                sh 'cp /export/www/installer-isos/SLE-15-SP1-Packages-x86_64-GM-DVD1.iso .'
                                break

                            case 'sles12':
                                sh 'cp /export/www/installer-isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso .'
                                sh 'cp /export/www/installer-isos/SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso .'
                                break

                            case 'sles11':
                                sh 'cp /export/www/installer-isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso .'
                                sh 'cp /export/www/installer-isos/SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso .'
                                sh 'cp /export/www/installer-isos/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso .'
                                sh 'cp /export/www/installer-isos/SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso .'
                                break
                        }
                    }
                }

                // Make a copy of test-framework for each test suite
                sh 'cp -al stacki/test-framework unit'
                sh 'cp -al stacki/test-framework integration_1'
                sh 'cp -al stacki/test-framework integration_2'
                sh 'cp -al stacki/test-framework integration_3'
                sh 'cp -al stacki/test-framework system'

                script {
                    // releases, develop branch, and branches ending in _cov get coverage reports
                    if (env.PLATFORM != 'sles11' && (env.IS_RELEASE == 'true' || env.GIT_BRANCH ==~ /develop|.*_cov/ || currentBuild.description ==~ /(?si).*\bcoverage\b.*/)) {
                        env.COVERAGE_REPORTS = 'true'

                        // A VM to combine all the coverage into a combined report
                        sh 'cp -al stacki/test-framework combine'

                        // A folder for the coverage reports to land in
                        sh 'mkdir coverage'
                    }
                    else {
                        env.COVERAGE_REPORTS = 'false'
                    }

                    // If we're SLES 11, use a matching SLES 12 Stacki pallet to be our frontend
                    // Note: Give it 20 minutes to show up (will usually take 10)
                    if (env.PLATFORM == 'sles11') {
                        retry(20) {
                            sh '''
                                SLES12_ISO_FILENAME=$(echo $ISO_FILENAME | sed -e 's|stacki-11.3|stacki-12.3|' -e 's|sles11.x86_64|sles12.x86_64|')
                                curl -H "X-JFrog-Art-Api:${ARTIFACTORY_PSW}" -sfSLO --retry 3 "https://sdartifact.td.teradata.com/artifactory/pkgs-external-snapshot-sd/$ART_ISO_PATH/sles-12.3/$GIT_BRANCH/$SLES12_ISO_FILENAME" || (STATUS=$? && sleep 60 && exit $STATUS)
                            '''
                        }
                    }
                }
            }

            post {
                always {
                    // Update the Stacki Builds website
                    build job: 'rebuild_stacki-builds_website', wait: false
                }

                failure {
                    // Notify the Slack #stacki-builds channel
                    slackSend(
                        channel: '#stacki-builds',
                        color: 'danger',
                        message: """\
                            Stacki failed to setup tests.
                            *Branch:* ${env.GIT_BRANCH}
                            *OS:* ${env.PLATFORM}
                            <${env.RUN_DISPLAY_URL}|View the pipeline job>
                        """.stripIndent(),
                        tokenCredentialId: 'slack-token-stacki'
                    )
                }
            }
        }

        stage('Tests') {
            parallel {
                stage('Unit') {
                    when {
                        not {
                            environment name: 'PLATFORM', value: 'sles11'
                        }
                    }

                    steps {
                        // Run the unit tests
                        dir('unit') {
                            // Give the tests up to 60 minutes to finish
                            timeout(60) {
                                script {
                                    try {
                                        if (env.COVERAGE_REPORTS == 'true') {
                                            sh './run-tests.sh --unit --coverage ../$ISO_FILENAME'
                                        }
                                        else {
                                            sh './run-tests.sh --unit ../$ISO_FILENAME'
                                        }
                                    }
                                    catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                                        // Make sure we clean up the VM
                                        dir('test-suites/unit') {
                                            sh 'vagrant destroy -f || true'
                                        }

                                        // Raise an error
                                        error 'Unit test-suite timed out'
                                    }
                                }
                            }
                        }
                    }

                    post {
                        always {
                            script {
                                // Record the test statuses for Jenkins
                                if (fileExists('unit/reports/unit-junit.xml')) {
                                    junit 'unit/reports/unit-junit.xml'
                                }

                                if (env.COVERAGE_REPORTS == 'true') {
                                    // Move the coverage report to the common folder
                                    sh 'mv unit/reports/unit coverage/'

                                    // Add the coverage data to the `combine` folder
                                    sh 'mv unit/reports/unit.coverage combine/reports/'
                                }
                            }
                        }
                    }
                }

                stage('Integration - Group 1') {
                    when {
                        not {
                            environment name: 'PLATFORM', value: 'sles11'
                        }
                    }

                    steps {
                        run_integration_test_steps('1', '3')
                    }

                    post {
                        always {
                            run_integration_test_post('1')
                        }
                    }
                }

                stage('Integration - Group 2') {
                    when {
                        not {
                            environment name: 'PLATFORM', value: 'sles11'
                        }
                    }

                    steps {
                        run_integration_test_steps('2', '3')
                    }

                    post {
                        always {
                            run_integration_test_post('2')
                        }
                    }
                }

                stage('Integration - Group 3') {
                    when {
                        not {
                            environment name: 'PLATFORM', value: 'sles11'
                        }
                    }

                    steps {
                        run_integration_test_steps('3', '3')
                    }

                    post {
                        always {
                            run_integration_test_post('3')
                        }
                    }
                }

                stage('System') {
                    steps {
                        // Run the system tests
                        dir('system') {
                            // Give the tests up to 90 minutes to finish
                            timeout(90) {
                                script {
                                    try {
                                        if (env.PLATFORM == 'sles11') {
                                            sh './run-tests.sh --system --extra-isos=../$ISO_FILENAME ../stacki-*-sles12.x86_64.disk1.iso'
                                        }
                                        else {
                                            if (env.COVERAGE_REPORTS == 'true') {
                                                sh './run-tests.sh --system --coverage ../$ISO_FILENAME'
                                            }
                                            else {
                                                sh './run-tests.sh --system ../$ISO_FILENAME'
                                            }
                                        }
                                    }
                                    catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                                        // Take a screenshots of the machine screens
                                        sh 'virsh screenshot $(cat .vagrant/machines/frontend/libvirt/id) screenshot-frontend.ppm'
                                        sh 'convert screenshot-frontend.ppm screenshot-frontend.png'
                                        archiveArtifacts 'screenshot-frontend.png'

                                        sh 'virsh screenshot $(cat .vagrant/machines/backend-0-0/libvirt/id) screenshot-backend-0-0.ppm'
                                        sh 'convert screenshot-backend-0-0.ppm screenshot-backend-0-0.png'
                                        archiveArtifacts 'screenshot-backend-0-0.png'

                                        sh 'virsh screenshot $(cat .vagrant/machines/backend-0-1/libvirt/id) screenshot-backend-0-1.ppm'
                                        sh 'convert screenshot-backend-0-1.ppm screenshot-backend-0-1.png'
                                        archiveArtifacts 'screenshot-backend-0-1.png'

                                        // Make sure we clean up the VM
                                        dir('test-suites/system') {
                                            sh 'vagrant destroy -f || true'
                                        }

                                        // Raise an error
                                        error 'System test-suite timed out'
                                    }
                                }
                            }
                        }
                    }

                    post {
                        always {
                            script {
                                // Record the test statuses for Jenkins
                                if (fileExists('system/reports/system-junit.xml')) {
                                    junit 'system/reports/system-junit.xml'
                                }

                                if (env.COVERAGE_REPORTS == 'true') {
                                    // Move the coverage report to the common folder
                                    sh 'mv system/reports/system coverage/'

                                    // Add the coverage data to the `combine` folder
                                    sh 'mv system/reports/system.coverage combine/reports/'
                                }
                            }
                        }
                    }
                }

                // Note: No more StackiOS until further notice
                // stage('StackiOS') {
                //     when {
                //         environment name: 'PLATFORM', value: 'redhat7'
                //         anyOf {
                //             branch 'develop'
                //             environment name: 'IS_RELEASE', value: 'true'
                //         }
                //     }
                //
                //     steps {
                //         build job: 'test_stackios', parameters: [
                //             string(name: 'STACKIOS_ISO', value: "http://stacki-builds.labs.teradata.com/stacki-isos/redhat7/stackios/${env.NORMALIZED_BRANCH}/${env.STACKIOS_FILENAME}"),
                //             string(name: 'STACKI_BRANCH', value: "${env.BRANCH_NAME}")
                //         ], wait: false
                //     }
                // }

                stage('Combine') {
                    when {
                        environment name: 'COVERAGE_REPORTS', value: 'true'
                    }

                    steps {
                        dir('combine/test-suites/unit') {
                            script {
                                // Create a VM to combine the coverage data
                                sh './set-up.sh ../../../$ISO_FILENAME'
                            }
                        }
                    }
                }
            }

            post {
                always {
                    script {
                        if (env.COVERAGE_REPORTS == 'true') {
                            // Combine the coverage data
                            dir('combine/test-suites/unit') {
                                sh '''
                                    set +e

                                    source ../../bin/activate

                                    vagrant ssh frontend -c "sudo -i coverage combine /export/reports/integration-*.coverage"
                                    vagrant ssh frontend -c "sudo -i coverage html -d /export/reports/integration/"
                                    vagrant ssh frontend -c "sudo -i mv /root/.coverage /export/reports/integration.coverage"

                                    vagrant ssh frontend -c "sudo -i coverage combine /export/reports/*.coverage"
                                    vagrant ssh frontend -c "sudo -i coverage html -d /export/reports/all/"

                                    ./tear-down.sh
                                    deactivate
                                '''
                            }

                            // Move our new `integration` and `all` coverage reports to the common folder
                            sh 'mv combine/reports/integration coverage/'
                            sh 'mv combine/reports/all coverage/'

                            // Publish the coverage reports
                            publishHTML(
                                allowMissing: true,
                                alwaysLinkToLastBuild: false,
                                keepAll: true,
                                reportDir: 'coverage',
                                reportFiles: 'all/index.html,unit/index.html,integration/index.html,system/index.html',
                                reportName: 'Code Coverage',
                                reportTitles: 'All,Unit,Integration,System'
                            )
                        }

                        // Update the Stacki Builds website
                        build job: 'rebuild_stacki-builds_website', wait: false
                    }
                }

                success {
                    // Tell github.com this commit passed tests
                    githubNotify(
                        context: "Test: ${env.PLATFORM}",
                        description: "tests succeeded",
                        status: 'SUCCESS'
                    )

                    script {
                        if (env.GIT_BRANCH != 'develop' && env.IS_RELEASE != 'true') {
                            // And the Slack #stacki-builds channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'good',
                                message: """\
                                    Stacki build and test has succeeded.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    *ISO:* ${env.ISO_FILENAME}
                                    *URL:* ${env.ART_URL}/pkgs-external-snapshot-sd/${env.ART_ISO_PATH}/${env.ART_OS}/${env.GIT_BRANCH}/${env.ISO_FILENAME}
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }
                    }
                }

                failure {
                    // Tell github.com this commit failed tests
                    githubNotify(
                        context: "Test: ${env.PLATFORM}",
                        description: "tests failed",
                        status: 'FAILURE'
                    )

                    // And the Slack #stacki-builds channel
                    slackSend(
                        channel: '#stacki-builds',
                        color: 'danger',
                        message: """\
                            Stacki tests have failed.
                            *Branch:* ${env.GIT_BRANCH}
                            *OS:* ${env.PLATFORM}
                            <https://sdvl3jenk015.td.teradata.com/blue/organizations/jenkins/stacki - ${env.PLATFORM}/detail/${env.JOB_BASE_NAME}/${env.BUILD_ID}/tests/|View the test results>
                        """.stripIndent(),
                        tokenCredentialId: 'slack-token-stacki'
                    )
                }
            }
        }

        stage('Promote') {
            when {
                anyOf {
                    branch 'develop'
                    environment name: 'IS_RELEASE', value: 'true'
                }
            }

            parallel {
                stage('Artifactory') {
                    steps {
                        // Figure out our Artifactory repo
                        script {
                            if (env.GIT_BRANCH == 'develop') {
                                env.ART_REPO = 'pkgs-external-qa-sd'
                            }
                            else {
                                env.ART_REPO = 'pkgs-external-released-sd'
                            }
                        }

                        // Upload the Stacki ISO to artifactory
                        rtUpload(
                            serverId: "td-artifactory",
                            spec: """
                                {
                                    "files": [{
                                        "pattern": "${env.ISO_FILENAME}",
                                        "target": "${env.ART_REPO}/${env.ART_ISO_PATH}/${env.ART_OS}/"
                                    }]
                                }
                            """
                        )
                    }

                    post {
                        success {
                            // Tell #stacki-builds we succeeded
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'good',
                                message: """\
                                    Stacki build and test has succeeded.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    *ISO:* ${env.ISO_FILENAME}
                                    *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_ISO_PATH}/${env.ART_OS}/${env.ISO_FILENAME}
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )

                            // Notify Slack of a new release
                            script {
                                if (env.IS_RELEASE == 'true') {
                                    slackSend(
                                        channel: '#stacki-announce',
                                        color: 'good',
                                        message: """\
                                            New Stacki ISO uploaded to Artifactory.
                                            *ISO:* ${env.ISO_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_ISO_PATH}/${env.ART_OS}/${env.ISO_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack-token-stacki'
                                    )
                                }
                            }

                            // Update the Stacki Builds website
                            build job: 'rebuild_stacki-builds_website', wait: false
                        }

                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki failed to upload to Artifactory.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }
                    }
                }

                stage('Amazon S3') {
                    when {
                        environment name: 'PLATFORM', value: 'redhat7'
                        environment name: 'IS_RELEASE', value: 'true'
                    }

                    steps {
                        withAWS(credentials:'amazon-s3-credentials') {
                            // Upload the Stacki ISO
                            s3Upload(
                                file: env.ISO_FILENAME,
                                bucket: 'teradata-stacki',
                                path: 'release/stacki/5.x/',
                                acl: 'PublicRead'
                            )
                            
                            // Note: For now, we no longer build StackiOS
                            // And the StackiOS ISO
                            // s3Upload(
                            //     file: env.STACKIOS_FILENAME,
                            //     bucket: 'teradata-stacki',
                            //     path: 'release/stacki/5.x/',
                            //     acl: 'PublicRead'
                            // )
                        }
                    }

                    post {
                        success {
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'good',
                                message: """\
                                    New Stacki ISO uploaded to Amazon S3.
                                    *Stacki:* http://teradata-stacki.s3.amazonaws.com/release/stacki/5.x/${env.ISO_FILENAME}
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }

                        failure {
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki ISO failed to upload to Amazon s3.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }
                    }
                }
            }
        }

        stage('Post Build') {
            when {
                anyOf {
                    branch 'develop'
                    environment name: 'IS_RELEASE', value: 'true'
                }
            }

            parallel {
                stage('BlackDuck Scan') {
                    steps {
                        // Get a copy of blackduck-scanner
                        sh 'git clone https://${TD_GITHUB}@github.td.teradata.com/software-manufacturing/stacki-blackduck-scanner.git'

                        // Now do the scan
                        dir ('stacki-blackduck-scanner') {
                            script {
                                if (env.IS_RELEASE == 'true') {
                                    sh './do-scan.sh release $PLATFORM $BLACKDUCK_TOKEN ../$ISO_FILENAME'
                                }
                                else {
                                    sh './do-scan.sh nightly $PLATFORM $BLACKDUCK_TOKEN ../$ISO_FILENAME'
                                }
                            }
                        }
                    }

                    post {
                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki Blackduck scan has failed.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }
                    }
                }

                stage('Build QCow2 Image') {
                    when {
                        not {
                            environment name: 'PLATFORM', value: 'sles11'
                        }
                    }

                    steps {
                        // Get a copy of stacki-packi
                        sh 'git clone https://${TD_GITHUB}@github.td.teradata.com/software-manufacturing/stacki-packi.git'

                        // Build the KVM image
                        dir ('stacki-packi') {
                            sh './do-build.sh ../$ISO_FILENAME'
                            sh 'mv stacki-*.qcow2 ../'
                        }

                        // Set an environment variable with the QCOW filename
                        script {
                            env.QCOW_FILENAME = findFiles(glob: 'stacki-*.qcow2')[0].name
                        }

                        // Upload the Stacki QCOW to artifactory
                        rtUpload(
                            serverId: "td-artifactory",
                            spec: """
                                {
                                    "files": [{
                                        "pattern": "${env.QCOW_FILENAME}",
                                        "target": "${env.ART_REPO}/${env.ART_QCOW_PATH}/${env.ART_OS}/"
                                    }]
                                }
                            """
                        )

                        // Releases of the Redhat version goes to amazon S3 too
                        script {
                            if (env.IS_RELEASE == 'true' && env.PLATFORM == 'redhat7') {
                                withAWS(credentials:'amazon-s3-credentials') {
                                    s3Upload(
                                        file: env.QCOW_FILENAME,
                                        bucket: 'teradata-stacki',
                                        path: 'release/stacki/5.x/',
                                        acl: 'PublicRead'
                                    )
                                }
                            }
                        }
                    }

                    post {
                        success {
                            // Notify Slack of a new release
                            script {
                                if (env.IS_RELEASE == 'true') {
                                    slackSend(
                                        channel: '#stacki-announce',
                                        color: 'good',
                                        message: """\
                                            New Stacki QCow2 image uploaded to Artifactory.
                                            *QCow2:* ${env.QCOW_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_QCOW_PATH}/${env.ART_OS}/${env.QCOW_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack-token-stacki'
                                    )

                                    if (env.PLATFORM == 'redhat7') {
                                        slackSend(
                                            channel: '#stacki-builds',
                                            color: 'good',
                                            message: """\
                                                New Stacki QCow2 image uploaded to Amazon S3.
                                                *QCow2:* ${env.QCOW_FILENAME}
                                                *URL:* http://teradata-stacki.s3.amazonaws.com/release/stacki/5.x/${env.QCOW_FILENAME}
                                            """.stripIndent(),
                                            tokenCredentialId: 'slack-token-stacki'
                                        )
                                    }
                                }
                            }

                            // Update the Stacki Builds website
                            build job: 'rebuild_stacki-builds_website', wait: false
                        }

                        failure {
                            // Notify the Slack #stacki-builds channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki QCow2 image build has failed.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }
                    }
                }

                stage('Build VMWare Image') {
                    agent {
                        label 'esxi_ova_builder'
                    }

                    when {
                        not {
                            environment name: 'PLATFORM', value: 'sles11'
                        }
                        not {
                            environment name: 'PLATFORM', value: 'sles15'
                        }
                    }

                    steps {
                        // Setup Artifactory access
                        rtServer(
                            id: "td-artifactory",
                            url: "${env.ART_URL}",
                            credentialsId: "d1a4e414-0526-4973-bea5-9d219d884f03",
                            timeout: 3600
                        )

                        // Get the Stacki ISO
                        rtDownload(
                            serverId: "td-artifactory",
                            spec: """
                                {
                                    "files": [{
                                        "pattern": "${env.ART_REPO}/${env.ART_ISO_PATH}/${env.ART_OS}/${env.ISO_FILENAME}",
                                        "flat": "true"
                                    }]
                                }
                            """
                        )

                        // Get a copy of stacki-packi
                        sh 'git clone https://${TD_GITHUB}@github.td.teradata.com/software-manufacturing/stacki-packi.git'

                        // Build the VMWare image
                        dir ('stacki-packi') {
                            sh './do-build.sh --esxi-host=sd-stacki-004.labs.teradata.com --esxi-user=root --format=vmware ../$ISO_FILENAME'
                            sh 'mv stacki-*-vmware.ova ../'
                        }

                        // Set an environment variable with the OVA filename
                        script {
                            env.VMWARE_FILENAME = findFiles(glob: 'stacki-*-vmware.ova')[0].name
                        }

                        // Upload the Stacki VMWare image to artifactory
                        rtUpload(
                            serverId: "td-artifactory",
                            spec: """
                                {
                                    "files": [{
                                        "pattern": "${env.VMWARE_FILENAME}",
                                        "target": "${env.ART_REPO}/${env.ART_OVA_PATH}/${env.ART_OS}/"
                                    }]
                                }
                            """
                        )

                        // Releases of the Redhat version goes to amazon S3 too
                        script {
                            if (env.IS_RELEASE == 'true' && env.PLATFORM == 'redhat7') {
                                withAWS(credentials:'amazon-s3-credentials') {
                                    s3Upload(
                                        file: env.VMWARE_FILENAME,
                                        bucket: 'teradata-stacki',
                                        path: 'release/stacki/5.x/',
                                        acl: 'PublicRead'
                                    )
                                }
                            }
                        }
                    }

                    post {
                        success {
                            // Notify Slack of a new release
                            script {
                                if (env.IS_RELEASE == 'true') {
                                    slackSend(
                                        channel: '#stacki-announce',
                                        color: 'good',
                                        message: """\
                                            New Stacki VMWare image uploaded to Artifactory.
                                            *OVA:* ${env.VMWARE_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_OVA_PATH}/${env.ART_OS}/${env.VMWARE_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack-token-stacki'
                                    )

                                    if (env.PLATFORM == 'redhat7') {
                                        slackSend(
                                            channel: '#stacki-builds',
                                            color: 'good',
                                            message: """\
                                                New Stacki VMWare image uploaded to Amazon S3.
                                                *OVA:* ${env.VMWARE_FILENAME}
                                                *URL:* http://teradata-stacki.s3.amazonaws.com/release/stacki/5.x/${env.VMWARE_FILENAME}
                                            """.stripIndent(),
                                            tokenCredentialId: 'slack-token-stacki'
                                        )
                                    }
                                }
                            }

                            // Update the Stacki Builds website
                            build job: 'rebuild_stacki-builds_website', wait: false
                        }

                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki VMWare image build has failed.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }

                        // Clean up after ourselves
                        always {
                            cleanWs()
                        }
                    }
                }

                stage('Build Virtualbox Image') {
                    agent {
                        label 'sd-stacki-021'
                    }

                    when {
                        not {
                            environment name: 'PLATFORM', value: 'sles11'
                        }
                    }

                    steps {
                        // Setup Artifactory access
                        rtServer(
                            id: "td-artifactory",
                            url: "${env.ART_URL}",
                            credentialsId: "d1a4e414-0526-4973-bea5-9d219d884f03",
                            timeout: 3600
                        )

                        // Get the Stacki ISO
                        rtDownload(
                            serverId: "td-artifactory",
                            spec: """
                                {
                                    "files": [{
                                        "pattern": "${env.ART_REPO}/${env.ART_ISO_PATH}/${env.ART_OS}/${env.ISO_FILENAME}",
                                        "flat": "true"
                                    }]
                                }
                            """
                        )

                        // Get a copy of stacki-packi
                        sh 'git clone https://${TD_GITHUB}@github.td.teradata.com/software-manufacturing/stacki-packi.git'

                        // Build the Virtualbox image
                        dir ('stacki-packi') {
                            sh './do-build.sh --format=vbox ../$ISO_FILENAME'
                            sh 'mv stacki-*-vbox.ova ../'
                        }

                        // Set an environment variable with the Virtualbox filename
                        script {
                            env.VBOX_FILENAME = findFiles(glob: 'stacki-*-vbox.ova')[0].name
                        }

                        // Upload the Stacki OVA to artifactory
                        rtUpload(
                            serverId: "td-artifactory",
                            spec: """
                                {
                                    "files": [{
                                        "pattern": "${env.VBOX_FILENAME}",
                                        "target": "${env.ART_REPO}/${env.ART_VBOX_PATH}/${env.ART_OS}/"
                                    }]
                                }
                            """
                        )

                        // Releases of the Redhat version goes to amazon S3 too
                        script {
                            if (env.IS_RELEASE == 'true' && env.PLATFORM == 'redhat7') {
                                withAWS(credentials:'amazon-s3-credentials') {
                                    s3Upload(
                                        file: env.VMWARE_FILENAME,
                                        bucket: 'teradata-stacki',
                                        path: 'release/stacki/5.x/',
                                        acl: 'PublicRead'
                                    )
                                }
                            }
                        }
                    }

                    post {
                        success {
                            // Notify Slack of a new release
                            script {
                                if (env.IS_RELEASE == 'true') {
                                    slackSend(
                                        channel: '#stacki-announce',
                                        color: 'good',
                                        message: """\
                                            New Stacki Virtualbox image uploaded to Artifactory.
                                            *OVA:* ${env.VBOX_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_VBOX_PATH}/${env.ART_OS}/${env.VBOX_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack-token-stacki'
                                    )

                                    if (env.PLATFORM == 'redhat7') {
                                        slackSend(
                                            channel: '#stacki-builds',
                                            color: 'good',
                                            message: """\
                                                New Stacki Virtualbox image uploaded to Amazon S3.
                                                *OVA:* ${env.VBOX_FILENAME}
                                                *URL:* http://teradata-stacki.s3.amazonaws.com/release/stacki/5.x/${env.VBOX_FILENAME}
                                            """.stripIndent(),
                                            tokenCredentialId: 'slack-token-stacki'
                                        )
                                    }
                                }
                            }

                            // Update the Stacki Builds website
                            build job: 'rebuild_stacki-builds_website', wait: false
                        }

                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-builds',
                                color: 'danger',
                                message: """\
                                    Stacki Virtualbox image build has failed.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack-token-stacki'
                            )
                        }

                        // Clean up after ourselves
                        always {
                            cleanWs()
                        }
                    }
                }
            }
        }

        stage('Merge') {
            when {
                branch 'feature/updates-*'
                environment name: 'PLATFORM', value: 'redhat7'
            }

            steps {
                // Poll the status of the other platforms' builds
                retry(20) {
                    sh '''
                        curl -s --user $JENKINS ${JOB_URL/redhat7/sles15}/lastBuild/api/json?tree=result | grep -q SUCCESS || (STATUS=$? && sleep 60 && exit $STATUS)
                        curl -s --user $JENKINS ${JOB_URL/redhat7/sles12}/lastBuild/api/json?tree=result | grep -q SUCCESS || (STATUS=$? && sleep 60 && exit $STATUS)
                        curl -s --user $JENKINS ${JOB_URL/redhat7/sles11}/lastBuild/api/json?tree=result | grep -q SUCCESS || (STATUS=$? && sleep 60 && exit $STATUS)
                    '''
                }

                dir('stacki') {
                    // Note: Will fail the stage if we can't fast-forward the
                    // commit, which will let us deal with merge issues manually

                    // Merge in the update branch via fast-forward
                    sh 'git checkout develop'
                    sh 'git merge --ff-only $GIT_BRANCH'
                    sh 'git push https://${GITHUB}@github.com/Teradata/stacki.git'

                    // Delete the old branch
                    sh 'git push https://${GITHUB}@github.com/Teradata/stacki.git --delete $GIT_BRANCH'
                }
            }

            post {
                failure {
                    slackSend(
                        channel: '#stacki-bot',
                        color: 'danger',
                        message: """\
                            Stacki merge has failed.
                            *Branch:* ${env.GIT_BRANCH}
                            <${env.RUN_DISPLAY_URL}|View the pipeline job>
                        """.stripIndent(),
                        tokenCredentialId: 'slack-token-stacki'
                    )
                }

                success {
                    slackSend(
                        channel: '#stacki-builds',
                        color: 'good',
                        message: """\
                            Stacki merge has succeeded.
                            *Branch:* ${env.GIT_BRANCH}
                        """.stripIndent(),
                        tokenCredentialId: 'slack-token-stacki'
                    )
                }
            }
        }
    }

    post {
        // Clean up after ourselves
        always {
            cleanWs()
        }
    }
}

def run_integration_test_steps(String group, String count) {
    // Run the integration tests
    dir("integration_$group") {
        // Give the tests up to 90 minutes to finish
        timeout(90) {
            script {
                try {
                    if (env.COVERAGE_REPORTS == 'true') {
                        sh "./run-tests.sh --integration --coverage --test-group-count=$count --test-group=$group ../\$ISO_FILENAME"
                    }
                    else {
                        sh "./run-tests.sh --integration --test-group-count=$count --test-group=$group ../\$ISO_FILENAME"
                    }
                }
                catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                    // Make sure we clean up the VM
                    dir('test-suites/integration') {
                        sh 'vagrant destroy -f || true'
                    }

                    // Raise an error
                    error "Integration Group $group test-suite timed out"
                }
            }
        }
    }
}

def run_integration_test_post(String group) {
    // Record the test statuses for Jenkins
    if (fileExists("integration_$group/reports/integration-junit.xml")) {
        junit "integration_$group/reports/integration-junit.xml"
    }

    if (env.COVERAGE_REPORTS == 'true') {
        // Add the coverage data to the `combine` folder
        sh "mv integration_$group/reports/integration.coverage combine/reports/integration-${group}.coverage"
    }
}
