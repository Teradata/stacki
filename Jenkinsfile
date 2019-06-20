pipeline {
    agent {
        label 'vagrant_kvm_builder'
    }

    environment {
        TD_GITHUB = credentials('cbaa2c3c-151e-4ba2-92ed-8f088762467b')
        ARTIFACTORY = credentials('d1a4e414-0526-4973-bea5-9d219d884f03')
        GITHUB_TOKEN = credentials('72702790-6cee-470b-94d0-1c3eb246a71d')
        BLACKDUCK_TOKEN = credentials('cb9c5430-f974-46e3-9d25-baeab4873db9')

        PIPELINE = env.JOB_NAME.split('/')[0].trim()
        PLATFORM = env.PIPELINE.split('-')[-1].trim()
        NORMALIZED_BRANCH = env.BRANCH_NAME.replaceAll('[/-]', '_')

        ART_URL = "https://sdartifact.td.teradata.com/artifactory"
        ART_ISO_PATH = "software-manufacturing/pallets/stacki"
        ART_QCOW_PATH = "software-manufacturing/kvm-images/stacki"
    }

    options {
        ansiColor('xterm')
        buildDiscarder(logRotator(daysToKeepStr: env.BRANCH_NAME == 'master' ? '365' : '20'))
        skipDefaultCheckout()
        timestamps()
    }

    triggers {
        // Nightly build of develop (at 3am)
        cron(env.BRANCH_NAME == 'develop' ? '0 11 * * *' : '')
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
                environment name: 'PLATFORM', value: 'sles12'
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
                    if (env.TAG_NAME ==~ /stacki-.*/ && env.BRANCH_NAME ==~ /master|support\/.*/) {
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
                            sh 'cp /export/www/installer-isos/CentOS-7-x86_64-Everything-1708.iso .'
                            sh 'cp /export/www/stacki-isos/redhat7/os/os-7.4_20171128-redhat7.x86_64.disk1.iso .'
                            env.OS_PALLET = 'os-7.4_20171128-redhat7.x86_64.disk1.iso'
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

                // Move the ISO into the root of the workspace
                sh 'mv stacki/stacki-*.iso .'

                // If we are Redhat, we will have a StackiOS ISO as well
                script {
                    if (env.PLATFORM == 'redhat7') {
                        sh 'mv stacki/stackios-*.iso .'
                    }
                }

                // Set an environment variable with the ISO filename
                script {
                    env.ISO_FILENAME = findFiles(glob: 'stacki-*.iso')[0].name
                }

                // Fingerprint the file, which Jenkins or our pipeline might use some day
                fingerprint "${env.ISO_FILENAME}"

                // If we are Redhat, fingerprint the StackiOS ISO as well
                script {
                    if (env.PLATFORM == 'redhat7') {
                        env.STACKIOS_FILENAME = findFiles(glob: 'stackios-*.iso')[0].name
                        fingerprint "${env.STACKIOS_FILENAME}"
                    }
                }
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
                        channel: '#stacki-bot',
                        color: 'danger',
                        message: """\
                            Stacki build has failed.
                            *Branch:* ${env.GIT_BRANCH}
                            *OS:* ${env.PLATFORM}
                            <${env.RUN_DISPLAY_URL}|View the pipeline job>
                        """.stripIndent(),
                        tokenCredentialId: 'slack_jenkins_integration_token'
                    )
                }
            }
        }

        stage('Upload') {
            when {
                not {
                    branch 'external/*'
                }
            }

            parallel {
                stage('Artifactory') {
                    steps {
                        // Setup Artifactory access
                        rtServer(
                            id: "td-artifactory",
                            url: "${env.ART_URL}",
                            credentialsId: "d1a4e414-0526-4973-bea5-9d219d884f03"
                        )

                        // Figure out our Artifactory OS
                        script {
                            env.ART_OS = [
                                'sles11': 'sles-11.3',
                                'sles12': 'sles-12.3',
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
                                channel: '#stacki-bot',
                                color: 'danger',
                                message: """\
                                    Stacki failed to upload to Artifactory.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack_jenkins_integration_token'
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

                        // If we are Redhat, we should have a StackiOS ISO as well
                        script {
                            if (env.PLATFORM == 'redhat7') {
                                // Create our MD5 of the ISO
                                sh 'md5sum $STACKIOS_FILENAME > $STACKIOS_FILENAME.md5'

                                // Make sure our web directory exists
                                sh 'mkdir -p /export/www/stacki-isos/redhat7/stackios/$NORMALIZED_BRANCH'

                                // Copy the files over
                                sh 'cp $STACKIOS_FILENAME /export/www/stacki-isos/redhat7/stackios/$NORMALIZED_BRANCH/'
                                sh 'cp $STACKIOS_FILENAME.md5 /export/www/stacki-isos/redhat7/stackios/$NORMALIZED_BRANCH/'
                            }
                        }
                    }

                    post {
                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-bot',
                                color: 'danger',
                                message: """\
                                    Stacki failed to copy to Stacki Builds website.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack_jenkins_integration_token'
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
                                sh 'cp /export/www/installer-isos/CentOS-7-x86_64-Everything-1708.iso .'
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
                sh 'cp -al stacki/test-framework integration'
                sh 'cp -al stacki/test-framework system'

                // Set up coverage reports, if needed
                script {
                    // releases, develop branch, and branches ending in _cov get coverage reports
                    if (env.PLATFORM ==~ 'sles12|redhat7' && (env.IS_RELEASE == 'true' || env.GIT_BRANCH ==~ /develop|.*_cov/)) {
                        env.COVERAGE_REPORTS = 'true'

                        // A VM to combine all the coverage into a combined report
                        sh 'cp -al stacki/test-framework combine'

                        // A folder for the coverage reports to land in
                        sh 'mkdir coverage'
                    }
                    else {
                        env.COVERAGE_REPORTS = 'false'
                    }
                }
            }

            post {
                always {
                    // Update the Stacki Builds website
                    build job: 'rebuild_stacki-builds_website', wait: false
                }

                failure {
                    // Notify the Slack #stacki-bot channel
                    slackSend(
                        channel: '#stacki-bot',
                        color: 'danger',
                        message: """\
                            Stacki failed to setup tests.
                            *Branch:* ${env.GIT_BRANCH}
                            *OS:* ${env.PLATFORM}
                            <${env.RUN_DISPLAY_URL}|View the pipeline job>
                        """.stripIndent(),
                        tokenCredentialId: 'slack_jenkins_integration_token'
                    )
                }
            }
        }

        stage('Tests') {
            parallel {
                stage('Unit') {
                    when {
                        anyOf {
                            environment name: 'PLATFORM', value: 'sles12'
                            environment name: 'PLATFORM', value: 'redhat7'
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

                stage('Integration') {
                    when {
                        anyOf {
                            environment name: 'PLATFORM', value: 'sles12'
                            environment name: 'PLATFORM', value: 'redhat7'
                        }
                    }

                    steps {
                        // Note: There is a race condition getting bridged networks
                        // when you kick off vagrant at the exact same time. So, cause
                        // a slight delay.
                        sleep 10

                        // Run the integration tests
                        dir('integration') {
                            // Give the tests up to 90 minutes to finish
                            timeout(90) {
                                script {
                                    try {
                                        if (env.COVERAGE_REPORTS == 'true') {
                                            sh './run-tests.sh --integration --coverage ../$ISO_FILENAME'
                                        }
                                        else {
                                            sh './run-tests.sh --integration ../$ISO_FILENAME'
                                        }
                                    }
                                    catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                                        // Make sure we clean up the VM
                                        dir('test-suites/integration') {
                                            sh 'vagrant destroy -f || true'
                                        }

                                        // Raise an error
                                        error 'Integration test-suite timed out'
                                    }
                                }
                            }
                        }
                    }

                    post {
                        always {
                            script {
                                // Record the test statuses for Jenkins
                                if (fileExists('integration/reports/integration-junit.xml')) {
                                    junit 'integration/reports/integration-junit.xml'
                                }

                                if (env.COVERAGE_REPORTS == 'true') {
                                    // Move the coverage report to the common folder
                                    sh 'mv integration/reports/integration coverage/'

                                    // Add the coverage data to the `combine` folder
                                    sh 'mv integration/reports/integration.coverage combine/reports/'
                                }
                            }
                        }
                    }
                }

                stage('System') {
                    steps {
                        sleep 20

                        // Run the system tests
                        dir('system') {
                            // Give the tests up to 90 minutes to finish
                            timeout(90) {
                                script {
                                    try {
                                        if (env.PLATFORM == 'sles11') {
                                            // If we're SLES 11, use a matching SLES 12 Stacki pallet to be our frontend
                                            // Note: Give it 20 minutes to show up (will usually take 10)
                                            retry(20) {
                                                sh 'curl -H "X-JFrog-Art-Api:${ARTIFACTORY_PSW}" -sfSLO --retry 3 "https://sdartifact.td.teradata.com/artifactory/pkgs-external-snapshot-sd/$ART_ISO_PATH/sles-12.3/$GIT_BRANCH/${ISO_FILENAME/%sles11.x86_64.disk1.iso/sles12.x86_64.disk1.iso}" || (STATUS=$? && sleep 60 && exit $STATUS)'
                                            }

                                            sh './run-tests.sh --system --extra-isos=../$ISO_FILENAME ${ISO_FILENAME/%sles11.x86_64.disk1.iso/sles12.x86_64.disk1.iso}'
                                        }
                                        else {
                                            sh './run-tests.sh --system ../$ISO_FILENAME'
                                        }
                                    }
                                    catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
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
                            }
                        }
                    }
                }

                stage('Combine') {
                    when {
                        environment name: 'COVERAGE_REPORTS', value: 'true'
                    }

                    steps {
                        sleep 30

                        dir('combine/test-suites/unit') {
                            // Create a VM to combine the coverage data
                            sh './set-up.sh ../../../$ISO_FILENAME'
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

                                    vagrant ssh frontend -c "sudo -i coverage combine /export/reports/*.coverage"
                                    vagrant ssh frontend -c "sudo -i coverage html -d /export/reports/all/"

                                    ./tear-down.sh
                                    deactivate
                                '''
                            }

                            // Move our new `all` coverage report to the common folder
                            sh 'mv combine/reports/all coverage/'

                            // Publish the coverage reports
                            publishHTML(
                                allowMissing: true,
                                alwaysLinkToLastBuild: false,
                                keepAll: true,
                                reportDir: 'coverage',
                                reportFiles: 'all/index.html,unit/index.html,integration/index.html',
                                reportName: 'Code Coverage',
                                reportTitles: 'All,Unit,Integration'
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

                    // And the Slack #stacki-bot channel
                    slackSend(
                        channel: '#stacki-bot',
                        color: 'good',
                        message: """\
                            Stacki build and test has succeeded.
                            *Branch:* ${env.GIT_BRANCH}
                            *OS:* ${env.PLATFORM}
                        """.stripIndent(),
                        tokenCredentialId: 'slack_jenkins_integration_token'
                    )
                }

                failure {
                    // Tell github.com this commit failed tests
                    githubNotify(
                        context: "Test: ${env.PLATFORM}",
                        description: "tests failed",
                        status: 'FAILURE'
                    )

                    // And the Slack #stacki-bot channel
                    slackSend(
                        channel: '#stacki-bot',
                        color: 'danger',
                        message: """\
                            Stacki tests have failed.
                            *Branch:* ${env.GIT_BRANCH}
                            *OS:* ${env.PLATFORM}
                            <https://sdvl3jenk015.td.teradata.com/blue/organizations/jenkins/stacki - ${env.PLATFORM}/detail/${env.JOB_BASE_NAME}/${env.BUILD_ID}/tests/|View the test results>
                        """.stripIndent(),
                        tokenCredentialId: 'slack_jenkins_integration_token'
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
                            // Notify Slack of a new release
                            script {
                                if (env.IS_RELEASE == 'true') {
                                    slackSend(
                                        channel: '#tdc-pallets',
                                        color: 'good',
                                        message: """\
                                            New Stacki ISO uploaded to Artifactory.
                                            *ISO:* ${env.ISO_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_ISO_PATH}/${env.ART_OS}/${env.ISO_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack_jenkins_integration_token'
                                    )

                                    slackSend(
                                        channel: '#stacki-announce',
                                        color: 'good',
                                        message: """\
                                            New Stacki ISO uploaded to Artifactory.
                                            *ISO:* ${env.ISO_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_ISO_PATH}/${env.ART_OS}/${env.ISO_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack_jenkins_integration_token'
                                    )
                                }
                            }

                            // Update the Stacki Builds website
                            build job: 'rebuild_stacki-builds_website', wait: false
                        }

                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-bot',
                                color: 'danger',
                                message: """\
                                    Stacki failed to upload to Artifactory.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack_jenkins_integration_token'
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

                            // And the StackiOS ISO
                            s3Upload(
                                file: env.STACKIOS_FILENAME,
                                bucket: 'teradata-stacki',
                                path: 'release/stacki/5.x/',
                                acl: 'PublicRead'
                            )
                        }
                    }

                    post {
                        success {
                            slackSend(
                                channel: '#stacki-bot',
                                color: 'good',
                                message: """\
                                    New Stacki ISOs uploaded to Amazon S3.
                                    *Stacki:* http://teradata-stacki.s3.amazonaws.com/release/stacki/5.x/${env.ISO_FILENAME}
                                    *StackiOS:* http://teradata-stacki.s3.amazonaws.com/release/stacki/5.x/${env.STACKIOS_FILENAME}
                                """.stripIndent(),
                                tokenCredentialId: 'slack_jenkins_integration_token'
                            )
                        }

                        failure {
                            slackSend(
                                channel: '#stacki-bot',
                                color: 'danger',
                                message: """\
                                    Stacki ISOs failed to upload to Amazon s3.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack_jenkins_integration_token'
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
                            sh './do-scan.sh $GIT_BRANCH $PLATFORM $BLACKDUCK_TOKEN ../stacki'
                        }
                    }

                    post {
                        failure {
                            // Notify the Slack #stacki-bot channel
                            slackSend(
                                channel: '#stacki-bot',
                                color: 'danger',
                                message: """\
                                    Stacki Blackduck scan has failed.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack_jenkins_integration_token'
                            )
                        }
                    }
                }

                stage('Build KVM QCow2') {
                    when {
                        anyOf {
                            environment name: 'PLATFORM', value: 'sles12'
                            environment name: 'PLATFORM', value: 'redhat7'
                        }
                    }

                    steps {
                        // Get a copy of kvm-builder
                        sh 'git clone https://${TD_GITHUB}@github.td.teradata.com/software-manufacturing/stacki-kvm-builder.git'

                        // Build the KVM image
                        dir ('stacki-kvm-builder') {
                            sh './do-build.sh ../$ISO_FILENAME'
                            sh 'mv stacki-*.qcow2 ../'
                        }

                        // Set an environment variable with the ISO filename
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
                                        channel: '#tdc-pallets',
                                        color: 'good',
                                        message: """\
                                            New Stacki QCow2 image uploaded to Artifactory.
                                            *QCow2:* ${env.QCOW_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_QCOW_PATH}/${env.ART_OS}/${env.QCOW_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack_jenkins_integration_token'
                                    )

                                    slackSend(
                                        channel: '#stacki-announce',
                                        color: 'good',
                                        message: """\
                                            New Stacki QCow2 image uploaded to Artifactory.
                                            *QCow2:* ${env.QCOW_FILENAME}
                                            *URL:* ${env.ART_URL}/${env.ART_REPO}/${env.ART_QCOW_PATH}/${env.ART_OS}/${env.QCOW_FILENAME}
                                        """.stripIndent(),
                                        tokenCredentialId: 'slack_jenkins_integration_token'
                                    )

                                    if (env.PLATFORM == 'redhat7') {
                                        slackSend(
                                            channel: '#stacki-bot',
                                            color: 'good',
                                            message: """\
                                                New Stacki QCow2 uploaded to Amazon S3.
                                                *QCow2:* ${env.QCOW_FILENAME}
                                                *URL:* http://teradata-stacki.s3.amazonaws.com/release/stacki/5.x/${env.QCOW_FILENAME}
                                            """.stripIndent(),
                                            tokenCredentialId: 'slack_jenkins_integration_token'
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
                                channel: '#stacki-bot',
                                color: 'danger',
                                message: """\
                                    Stacki KVM build has failed.
                                    *Branch:* ${env.GIT_BRANCH}
                                    *OS:* ${env.PLATFORM}
                                    <${env.RUN_DISPLAY_URL}|View the pipeline job>
                                """.stripIndent(),
                                tokenCredentialId: 'slack_jenkins_integration_token'
                            )
                        }
                    }
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
