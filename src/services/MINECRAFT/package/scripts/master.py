import os
import sys
import urllib
from os import path
from resource_management import *

class Master(Script):

    def install(self, env):
        import params

        env.set_params(params)

        User(
            params.minecraft_user,
            password=params.hashed_minecraft_password,
            action="create", shell="/bin/bash"
        )

        Directory(
            params.installation_path,
            action="create",
            recursive=True,
            owner=params.minecraft_user
        )

        self.install_packages(env)

        self.download_to(params.installation_source, params.installation_path)

        Execute(format("""
            cd {params.installation_path}
            git config --global --unset core.autocrlf;
            java -jar BuildTools.jar;
            """),
            user=params.minecraft_user
        )

        TemplateConfig(
            path.join(params.installation_path, 'eula.txt.j2'),
            owner=params.minecraft_user, mode=0644
        )

        File(
            path.join(params.installation_path, 'permissions.yml'),
            content=params.permissions,
            owner=params.minecraft_user
        )

    def start(self, env):
        import params
        env.set_params(params)

        self.configure(env)

        Execute(
            format("cd {params.installation_path}; java -Xms{params.minimum_ram} -Xmx{params.maximum_ram} -jar spigot.jar -o true"),
            user=params.minecraft_user
        )

    def stop(self, env):
        import params

        Execute(
            "",
            user=params.minecraft_user
        )

    def configure(self, env):
        pass
        #TemplateConfig(
            #params.greenplum_initsystem_config_file,
            #owner=params.admin_user, mode=0644
        #)

    def status(self, env):
        import params

    def download_to(self, url, destination):
        import params

        try:
            filename = path.basename(url)
            tmp_path = path.join(params.tmp_dir, filename)

            urllib.urlretrieve(url, tmp_path)

            os.rename(tmp_path, path.join(destination, filename))
        except IOError:
            return None

if __name__ == "__main__":
    Master().execute()
