// vim: set ft=groovy :

pipeline {
    agent any
    triggers {
        cron(env.BRANCH_NAME == 'master' ? '*/15 * * * *': '')
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '1000', daysToKeepStr: '60'))
        disableConcurrentBuilds()
    }
    stages {
        stage('Prepare') {
            when {
                branch 'master'
            }
            steps {
                sh "pipenv install"
            }
        }
        stage('PukiWiki') {
            when {
                branch 'master'
            }
            steps {
                sh "pipenv run -- python3 pukiwiki-crawler.py crawl"
            }
        }
        stage('Paragate') {
            when {
                branch 'master'
            }
            steps {
                sh 'pipenv run -- python3 paragate-crawler.py crawl'
            }
        }
    }
    post {
        failure {
            slackMessage ':oikari: heineken-crawler FAILED :oikari:', true, 'danger'
        }
    }
}

def slackMessage(message, includeInfo, color=null) {
    final GITHUB_URL = "https://github.com/kmc-jp/heineken-crawler/"
    if (includeInfo) {
        def info = "<${env.BUILD_URL}|${env.JOB_NAME} - #${env.BUILD_NUMBER}> (<${GITHUB_URL}|GitHub>)"
        slackSend color: color, message: "${message}: ${info}"
    } else {
        slackSend message: message
    }
}
