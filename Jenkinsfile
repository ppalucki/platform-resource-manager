pipeline {
    agent any
    stages {
        stage("Run flake8 on PRM") {
            streps {
                sh'''
                cd prm
                tox -e flake8
                '''
            }
        }
        stage("Build owca-prm.pex") {
            steps {
                sh'''
                cd prm
                tox -e package
                '''
                stash(name: "wrappers", includes: "dist/**")
                archiveArtifacts(artifacts: "dist/**")
            }
            post {
                always {
                    sh '''
                    rm -fr dist
                    '''
                }
            }
        }
    }
}
