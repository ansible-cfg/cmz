@Grapes([
    @Grab(group='org.yaml', module='snakeyaml', version='1.20')
])

import hudson.FilePath
import org.yaml.snakeyaml.Yaml
import org.yaml.snakeyaml.constructor.CustomClassLoaderConstructor

// Class to load the YAML
class ProjectConfig {
    String project
    String repo = "ssh://git@enterprise-stash.hybris.com:7999/hcs-pdo-sre/mgmtzone_automation.git"
    String repo_credentials = "bitbucket_ssh_key"
    String rundeck_repo = "ssh://git@enterprise-stash.hybris.com:7999/hcs-pdo-aba/ansible-code.git"
    String rundeck_repo_credentials = "rundeck_scm_ssh_key"
    String monitoring_repo = "ssh://git@enterprise-stash.hybris.com:7999/hcs-pdo-mon/project-x.git"
    String monitoring_repo_credentials = "monitoring_scm_ssh_key"
    String branch = "master"
    String playbook
    String ansible_ssh_key = "ansible_ssh_key"
    String ansible_vault_passwd = "ansible_vault_passwd"
    String monitoring_ansible_ssh_key = "monitoring_ansible_ssh_key"
    String monitoring_ansible_vault_passwd = "monitoring_ansible_vault_passwd"
    String service_user
    ArrayList parameters = []
}

// JobDSL Template
class DeployTemplate {
    static boolean isSecret(name) {
        return name.matches(".*(?i:key|pass|secret).*")
    }

    // create deployment job except rundeck
    static void create(job, config) {
        job.with {
            description("Deploy ${config.project}. This job is managed via JobDSL; any manual changes will be lost.")

            wrappers {
                preBuildCleanup()
                colorizeOutput()
            }

            logRotator {
                artifactDaysToKeep(7)
                daysToKeep(90)
            }

            parameters {
                stringParam('GIT_BRANCH', config.branch, 'Git Branch to be used for Ansible repo')
            }

            for (item in config.parameters) {
                parameters {
                    if (isSecret(item)) {
                        nonStoredPasswordParam(item, 'Secret that gets passed to Ansible')
                    } else {
                        stringParam(item, '', 'Variable that gets passed to Ansible')
                    }
                }
            }

            scm {
                git {
                    remote {
                        url(config.repo)
                        credentials(config.repo_credentials)
                    }
                    branch('$GIT_BRANCH')
                }
            }

            steps {
                shell('${WORKSPACE}/Inventory.py --static > ${WORKSPACE}/Generated_Ansible_Inventory')
            }

            steps {
                ansiblePlaybook(config.playbook) {
                    inventoryPath('Generated_Ansible_Inventory')
                    credentialsId(config.ansible_ssh_key)
                    vaultCredentialsId(config.ansible_vault_passwd)
                    colorizedOutput(true)
                    for (item in config.parameters) {
                        extraVars {
                            extraVar(item, "\$" + item, isSecret(item))
                        }
                    }
                }
            }
        }
    }

    // create rundeck deployment job
    static void createRundeckJob(job, config, dataCenter, env) {
        job.with {
            description("Deploy ${config.project}. This job is managed via JobDSL; any manual changes will be lost.")

            wrappers {
                preBuildCleanup()
                colorizeOutput()
            }

            logRotator {
                artifactDaysToKeep(7)
                daysToKeep(90)
            }

            parameters {
                stringParam('GIT_BRANCH', '', 'Git Branch to be used for Rundeck repo')
            }

            for (item in config.parameters) {
                parameters {
                    stringParam(item, '', 'Variable that gets passed to Rundeck installation script')
                }
            }

            scm {
                git {
                    remote {
                        url(config.rundeck_repo)
                        credentials(config.rundeck_repo_credentials)
                    }
                    branch('$GIT_BRANCH')
                }
            }

            steps {
                shell("sudo -E -H -u ${config.service_user} bash -c '" +
                        "source /home/${config.service_user}/rundeck/bin/activate; " +
                        "ansible --version;" +
                        "./install_rundeck.sh -e${env[0]} -dc${dataCenter} --branch \$GIT_BRANCH" +
                        "'")
            }
        }
    }
   
    // create monitoring configration job
    static void createMonitoringJob(job, config, dataCenter) {
       String service_user = "svc_" + dataCenter + "ansible_mon"

        job.with {
            description("Deploy ${config.project}. This job is managed via JobDSL; any manual changes will be lost.")

            wrappers {
                preBuildCleanup()
                colorizeOutput()
            }

            logRotator {
                artifactDaysToKeep(7)
                daysToKeep(90)
            }

            parameters {
                stringParam('GIT_BRANCH', config.branch, 'Git Branch to be used for Ansible repo')
            }

            scm {
                git {
                    remote {
                        url(config.monitoring_repo)
                        credentials(config.monitoring_repo_credentials)
                    }
                    branch('$GIT_BRANCH')
                }
            }

            triggers {
                    cron('H 12 * * *')
            }

            steps {
                shell("umask 022;" +
                      "virtualenv venv;" +
                      "source venv/bin/activate;" +
                      "pip install -r requirements.txt;" +
                      "touch request_cache.sqlite;" +
                      "ln -s ${dataCenter}-hybris.yml hybris.yml;" +
                      "./inventory.py --list --refresh"
                )        
            }
            
            steps {
                ansiblePlaybook(config.playbook) {
                    ansibleName('2.5.4')
                    inventoryPath('./inventory.py')
                    credentialsId(config.monitoring_ansible_ssh_key)
                    vaultCredentialsId(config.monitoring_ansible_vault_passwd)
                    colorizedOutput(true)
                    tags('update_icinga2_config,grafana')
                }
            }
        }
    }
}

def getEnvironment() {
    def hostName = InetAddress.localHost.getHostName()
    String[] str
    splitHostName = hostName.split('-')
    def dataCenter = splitHostName[0]
    def env = splitHostName[2][-1..-1]
    switch (env) {
        case "p":
            env = "prd"
            break
        case "s":
            env = "stg"
            break
        case "d":
            env = "dev"
            break
        case "q":
            env = "qa"
            break
        default:
            env = "SOMETHING_WENT_WRONG"
            break
    }
    return [dataCenter, env]
}

def getConfigFiles(dir) {
    if (!dir.isDirectory()) {
        return [:]
    }
    def fileList = dir.list('*.yml')
    def fileMap = fileList.collectEntries {
        [it.getName() , it]
    }
    return fileMap
}

void createJobs(String dataCenter, String env) {
    def constr = new CustomClassLoaderConstructor(this.class.classLoader)
    def yaml = new Yaml(constr)

    // Build a list of all config files ending in .yml
    def cwd = hudson.model.Executor.currentExecutor().getCurrentWorkspace().absolutize()
    def configsGlobal = getConfigFiles(new FilePath(cwd, 'jobdsl/configs/'))
    def configsDC     = getConfigFiles(new FilePath(cwd, 'jobdsl/configs/' + dataCenter))
    def configsDCEnv  = getConfigFiles(new FilePath(cwd, 'jobdsl/configs/' + dataCenter + '/' + env))
    def configFiles = configsGlobal + configsDC + configsDCEnv
    println configFiles.values().toString().replace(',', '\n')

    // Create/update a pull request job for each config file
    configFiles.values().each { file ->
        def projectConfig = yaml.loadAs(file.readToString(), ProjectConfig.class)
        if (file ==~ /^.*\/param-rundeck.yml$/ ) {
            DeployTemplate.createRundeckJob(job(projectConfig.project), projectConfig, dataCenter, env)
        } 
        else if (file ==~ /^.*\/param-monitoring.yml$/ ){ 
            DeployTemplate.createMonitoringJob(job(projectConfig.project), projectConfig, dataCenter)
        }
        else {
            DeployTemplate.create(job(projectConfig.project), projectConfig)
        }
    }
}

// MAIN
def (dataCenter, env) = getEnvironment()

createJobs(dataCenter, env)
