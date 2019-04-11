pipeline {
    agent any
    environment {
        PLAYBOOK='prm/owca/workloads/run_workloads.yaml'
        INVENTORY='prm/demo_scenarios/common/inventory.yaml'
        LLC_INVENTORY='prm/demo_scenarios/complex_llc.0/inventory.yaml'
        MEMBW_INVENTORY='prm/demo_scenarios/complex_mbw.0/inventory.yaml'
        PROMETHEUS='http://100.64.176.12:9090' 
        LLC_LABELS="{additional_labels: {build_number: \"${BUILD_NUMBER}\", build_node_name: \"${NODE_NAME}\", build_commit: \"${GIT_COMMIT}\", scenario: \"complex_llc.0\"}}"
        MBW_LABELS="{additional_labels: {build_number: \"${BUILD_NUMBER}\", build_node_name: \"${NODE_NAME}\", build_commit: \"${GIT_COMMIT}\", scenario: \"complex_mbw.0\"}}"
    }
    options {
        disableConcurrentBuilds()
        timeout(time: 5, unit: 'MINUTES')
    }
    parameters {
        booleanParam(name: 'REDEPLOY_PEX', defaultValue: false, description: 'Redeploy pex this value')
        booleanParam(name: 'LLC', defaultValue: false, description: 'Run LLC experiment')
        booleanParam(name: 'MB', defaultValue: false, description: 'Run LLC experiment')
    }
    stages {
        stage('Redeploy pex') {
            when {
                expression { return params.REDEPLOY_PEX }
            }
            stages {

                stage("Prepare venv") {
                    steps {
                        sh'''
                        cd prm
                        make venv
                        '''
                    }
                }
                stage("Run flake8 on PRM") {
                    steps {
                        sh'''
                        cd prm
                        make flake8
                        '''
                    }
                }
                stage("Run PRM unit tests") {
                    steps {
                        sh'''
                        cd prm
                        make unit
                        '''
                    }
                }
                stage("Build owca-prm.pex") {
                    steps {
                        sh'''
                        cd prm
                        make package
                        '''
                        // stash(name: "owca-prm", includes: "prm/dist/**")
                        // archiveArtifacts(artifacts: "prm/dist/**")
                    }
                    post {
                        always {
                            sh '''
                            rm -fr prm/dist
                            '''
                        }
                    }
                }
            }
        }
        stage("Prepare aurora cluster") {
            steps {
                sh'''
                mkdir -p ${HOME}/.aurora
                cp ${WORKSPACE}/prm/demo_scenarios/common/aurora-clusters.json  ${HOME}/.aurora/clusters.json
                '''
            }
        }
        stage("Run LLC experiment") {
            steps {
                dir('prm/owca/workloads'){
                    echo 'start baseline'
                    sh 'ansible-playbook -v -i ${WORKSPACE}/${LLC_INVENTORY} -i ${WORKSPACE}/${INVENTORY} --tags=twemcache_mutilate,redis_rpc_perf,cassandra_stress--cassandra -e "${LLC_LABELS}" ${WORKSPACE}/${PLAYBOOK}' 
                    sleep 60
                    echo 'start contender'
                    sh 'ansible-playbook -v -i ${WORKSPACE}/${LLC_INVENTORY} -i ${WORKSPACE}/${INVENTORY} --tags=cassandra_stress--stress -e "${LLC_LABELS}" ${WORKSPACE}/${PLAYBOOK}'
                    sleep 30
                }
                dir('prm'){
                    echo 'calcuate results'
                    sh 'pipenv run python calculate_accuracy.py --prometheus ${PROMETHEUS} ${BUILD_NUMBER}'
                }
            }
            post {
                always {
                    echo 'stop workloads'
                    sh 'ansible-playbook -v -i ${WORKSPACE}/${INVENTORY} --tags=clean_jobs ${WORKSPACE}/${PLAYBOOK}'
                }
            }
        }
        stage("Clean all jobs") {
            steps {
                dir('prm/owca/workloads') {
                    sh 'ansible-playbook -v -i ${WORKSPACE}/${INVENTORY} --tags=clean_jobs ${WORKSPACE}/${PLAYBOOK}'
                }
            }
        }
        /*
        stage("Run Memory Bandwidth experiment") {
            steps {
                sh '''
                ansible-playbook -vvv -l ${PRM_SUT} -i ${WORKSPACE}${MEMBW_INVENTORY} -i ${DEFAULT_INVENTORY} --tags=specjbb,tensorflow_benchmark_prediction,tensorflow_benchmark_train,cassandra_stress -e "${MBW_LABELS}" ${WORKSPACE}${PLAYBOOK}
                ansible-playbook -vvv -l ${PRM_SUT} -i ${WORKSPACE}${MEMBW_INVENTORY} -i ${DEFAULT_INVENTORY} --tags=tensorflow_benchmark_prediction -e "${MBW_LABELS}" ${WORKSPACE}${PLAYBOOK}
                '''
            }
        }
        */
    }
}
