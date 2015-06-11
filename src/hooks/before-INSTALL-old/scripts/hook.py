from resource_management import *
from repository_initialization import *
from shared_initialization import *

class BeforeInstallHook(Hook):
    def hook(self, env):
        import params

        create_repositories()
        install_packages() # Install setup_java dependencies
        setup_java()

if __name__ == "__main__":
    BeforeInstallHook().execute()