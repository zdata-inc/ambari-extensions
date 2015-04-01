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
            mv spigot-*.jar spigot.jar;
            mv craftbukkit-*.jar craftbukkit.jar;
            """),
            user=params.minecraft_user
        )

        Execute(
            format("""
                cd {params.installation_path};
                git clone https://github.com/Ahtenus/minecraft-init.git;
                cd minecraft-init;
            """),
            user=params.minecraft_user
        )

        minecraft_init_path = path.join(params.installation_path, 'minecraft-init', 'minecraft')
        Execute(format("""
            ln -s {minecraft_init_path} /etc/init.d/minecraft;
            chmod +x /etc/init.d/minecraft;
        """))

        TemplateConfig(
            path.join(params.installation_path, 'minecraft-init', 'config'),
            template_tag="init",
            owner=params.minecraft_user, mode=0644
        )

    def start(self, env):
        import params
        env.set_params(params)

        self.configure(env)

        Execute(
            "service minecraft start"
            #format("cd {params.installation_path}; java -Xms{params.minimum_ram} -Xmx{params.maximum_ram} -jar spigot.jar -o true"),
        )

    def stop(self, env):
        import params

        Execute(
            "",
            user=params.minecraft_user
        )

    def configure(self, env):
        TemplateConfig(
            path.join(params.installation_path, 'eula.txt'),
            owner=params.minecraft_user, mode=0644
        )

        File(
            path.join(params.installation_path, 'permissions.yml'),
            content=params.permissions,
            owner=params.minecraft_user
        )

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
