# coding: utf-8
import logging
import getpass
import re
import os
import paramiko
from . import BaseTask
from cactus.scp import SCPClient
import yaml


class DeployTask(BaseTask):
    """
    Deploy project
    """

    local_settings = {}
    config = {}
    helptext_short = "deploy [target] [--build=yes|no]: " \
                     "deploy project to the given target."

    @classmethod
    def conf(cls, key, default=None):
        return cls.local_settings.get(key, cls.config.get(key, default))

    @classmethod
    def run(cls, *args, **kwargs):
        if len(args) > 2:
            print cls.usage()
            return

        do_build = True
        target = "default"
        if len(args) > 1:
            m1 = re.match(r'--build=(yes|no)', args[0], re.I)
            m2 = re.match(r'--build=(yes|no)', args[1], re.I)
            if m1:
                target = args[1]
                do_build = m1.group(1).lower() == "yes"
            else:
                target = args[0]
                if m2:
                    do_build = m2.group(1).lower() == "yes"
        elif len(args) == 1:
            m1 = re.match(r'--build=(yes|no)', args[0], re.I)
            if m1:
                do_build = m1.group(1).lower() == "yes"
            else:
                target = args[0]

        try:
            cls.local_settings = yaml.load(
                open(os.path.join(os.getcwd(), "deploy.yml"), 'r')
            ).get(target)
        except Exception, e:
            cls.local_settings = {}
            logging.warn("No local deploy.yml present or error parsing it:\n{0}".format(e))

        from cactus import site
        site = site.Site(os.getcwd())
        site.verify()
        cls.config = site.config.get("deploy").get(target, "default")
        deployment_type = cls.conf("type", "ssh")

        def createSSHClient(server, port=22, user=None, password=None, privkey=None):
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                server,
                port=port,
                username=user,
                password=password,
                key_filename=privkey,
            )
            return client

        if do_build:
            print "Building site..."
            site.build(dist=True)
            site.call_plugin_method("preDeploy")
        print u"Deploying to {0}...".format(target)

        if deployment_type == "ssh":
            host = cls.conf("host")
            port = int(cls.conf("port", 22))
            print "Connecting to {0}...".format(host)

            auth_type = cls.conf("auth", "password")

            try:
                from win32com.shell import shellcon, shell
                homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
            except ImportError:
                homedir = os.path.expanduser("~")

            if auth_type == "public-key":
                try:
                    ssh = createSSHClient(
                        host,
                        port=port,
                        user=cls.conf("user"),
                        privkey=cls.conf("private_key", "{home}/.ssh/id_rsa").format(home=homedir),
                    )
                except paramiko.PasswordRequiredException:
                    ssh = createSSHClient(
                        host,
                        port=port,
                        user=cls.conf("user"),
                        privkey=cls.conf("private_key", "{home}/.ssh/id_rsa").format(home=homedir),
                        password=getpass.getpass(prompt="Please enter your password: "),
                    )
            else:
                user = cls.conf("user")
                if not user:
                    user = raw_input("Please enter your username: ")

                ssh = createSSHClient(
                    host,
                    port=port,
                    user=user,
                    password=getpass.getpass(prompt="Please enter your password: ")
                )

            scp = SCPClient(ssh.get_transport())

            dist_dir = site.paths['dist']
            for file in os.listdir(dist_dir):
                f = os.path.join(dist_dir, file)
                scp.put(f, remote_path=cls.conf("path"), recursive=os.path.isdir(f))
            site.call_plugin_method("postDeploy")
        else:
            logging.warn("Deployment type '{0}' is not implemented!".format(deployment_type))
