# coding: utf-8
import fnmatch
import logging
import getpass
import boto
import sys
from cactus.s3.utils import fileList
import re
import os
import paramiko
import yaml
from . import BaseTask
from cactus.s3.file import File
from paramiko import SFTPClient
from cactus.utils import to_unix_path


class DeployTask(BaseTask):
    """
    Deploy project
    """

    local_settings = {}
    config = {}
    helptext_short = "deploy [target] [--build=yes|no] [--runtests=yes|no]: " \
                     "deploy project to the given target."

    @classmethod
    def conf(cls, key, default=None):
        return cls.local_settings.get(key, cls.config.get(key, default))

    @classmethod
    def run(cls, *args, **kwargs):
        if len(args) > 3:
            print cls.usage()
            return

        do_build = True
        run_tests = False
        target = "default"

        for arg in args:
            m1 = re.match(r'--build=(yes|no)', arg, re.I)
            m2 = re.match(r'--runtests=(yes|no)', arg, re.I)
            if m1:
                do_build = m1.group(1).lower() == "yes"
            elif m2:
                run_tests = m2.group(1).lower() == "yes"
            else:
                target = arg

        try:
            cls.local_settings = yaml.load(
                open(os.path.join(os.getcwd(), "deploy.yml"), 'r')
            ).get(target)
        except Exception, e:
            cls.local_settings = {}
            logging.warn("No local deploy.yml present or error parsing it:\n{0}".format(e))

        from cactus import site as cactus_site
        site = cactus_site.Site(os.getcwd())
        site.verify()
        cls.config = site.config.get("deploy").get(target, "default")

        deployment_type = cls.conf("type", "ssh")
        discard_files = cls.conf("discard", [])

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

        if do_build or run_tests:
            print "Building site..."
            site.build(dist=True)
            site.call_plugin_method("preDeploy")
            if run_tests:
                if not site.run_tests():
                    logging.error("Not all tests ran successfully! Exiting...")
                    return
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

            scp = SFTPClient.from_transport(ssh.get_transport())
            dist_dir = os.path.abspath(site.paths['dist'])
            remote_base = cls.conf("path")

            for (path, dirs, files) in os.walk(dist_dir):
                remote_path = path.replace(dist_dir, '')
                remote_path = re.sub(r'^/', '', remote_path)
                remote_path = re.sub(r'^\\', '', remote_path)
                for d in dirs:
                    rdir = to_unix_path(os.path.join(remote_base, remote_path, d))
                    try:
                        scp.stat(rdir)
                    except IOError:
                        scp.mkdir(rdir)
                for f in files:
                    src = os.path.abspath(os.path.join(path, f))
                    dest = to_unix_path(os.path.join(remote_base, remote_path, f))
                    discard = False
                    for pattern in discard_files:
                        d = "/**/{0}".format(pattern)
                        if fnmatch.fnmatch(dest, d):
                            discard = True
                    if not discard:
                        logging.info("Copying {0} => {1}".format(src, dest))
                        scp.put(
                            src,
                            dest
                        )
                    else:
                         logging.info("DISCARD: {0}".format(src))

            site.call_plugin_method("postDeploy")
        elif deployment_type == "s3":
            key = cls.conf("s3_access_key")
            secret = cls.conf("s3_secret_key")
            if not key:
                key = raw_input("Please enter Amazon AWS key: ")
            if not secret:
                secret = raw_input("Please enter Amazon AWS Secret Key: ")
            connection = boto.connect_s3(key.strip(), secret.strip())
            try:
                buckets = connection.get_all_buckets()
            except:
                logging.error('Invalid login credentials, please try again...')
                return
            bucket = cls.conf("s3_bucket")
            if not bucket:
                bucket = raw_input("S3 bucket name (www.yoursite.com): ").strip().lower()
            if bucket not in [b.name for b in buckets]:
                if raw_input('Bucket does not exist, create it? (y/n): ') == 'y':
                    try:
                        created_bucket = connection.create_bucket(bucket, policy='public-read')
                    except boto.exception.S3CreateError, e:
                        logging.error('Bucket with name {0} already is used by someone else, please try again with another name.'.format(bucket))
                        return
                    created_bucket.configure_website('index.html', 'error.html')

            try:
                buckets = connection.get_all_buckets()
            except:
                logging.error('Invalid login credentials, please try again...')
                return

            selected_bucket = None
            for b in buckets:
                if b.name == bucket:
                    selected_bucket = b
            if selected_bucket:
                dist_dir = site.paths['dist']
                for f in fileList(dist_dir, relative=True):
                    s3_file = File(site, f, cls.conf("s3_site_domain"))

                    discard = False
                    for pattern in discard_files:
                        if fnmatch.fnmatch(f, pattern):
                            discard = True
                    if not discard:
                        s3_file.upload(selected_bucket)
                    else:
                         logging.info("DISCARD: {0}".format(f))

            site.call_plugin_method("postDeploy")
            logging.info("Deployment complete. Please check your site at:\nhttp://{0}/".format(cls.conf("s3_site_domain")))
        else:
            logging.warn("Deployment type '{0}' is not implemented!".format(deployment_type))
