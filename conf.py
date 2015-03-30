#!/usr/bin/env python
#  -*- coding: utf-8 -*- 
#ygavrilenko@gmail.com

import ConfigParser
import os


def check_config():
    if os.path.isfile('./config.ini'):
        return True
#    print "[Error]\t\tconfig.ini not found in current directory"
    return False


def denc(password):
    result = [chr(i) for i in [int((int(hex(ord(i)), 16) + 0x4) ^ 0xb) for i in password]]
    return ''.join(result)


def load_config():
    # load and parse config, return list of dictionary
    settings_main, settings_svn, settings_samba = {}, {}, {}
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    settings_main["local_storage"] = config.get("main", "local_storage")
    settings_main["log_dir"] = config.get("main", "log_dir")
    settings_svn["repository"] = config.get("repository", "svn_url")
    settings_svn["svn_username"] = config.get("repository", "svn_username")
    settings_svn["svn_password"] = denc(config.get("repository", "svn_password"))
    settings_samba["smb_server"] = config.get("samba", "smb_server")
    settings_samba["smb_username"] = config.get("samba", "smb_username")
    settings_samba["smb_password"] = denc(config.get("samba", "smb_password"))

    return settings_main, settings_svn, settings_samba


def show_config():
    if not check_config():
        print "[ERROR]\tConfig not found"
        return 1
    settings_main, settings_svn, settings_samba = load_config()
    config = [('OS username', os.environ['USERNAME'])]
    config.append(('Hostname', os.environ['COMPUTERNAME']))
    config.append(('Storage', settings_main['local_storage']))
    config.append(('Log directory', settings_main['log_dir']))
    config.append(('Repository', settings_svn['repository']))
    config.append(('Svn username', settings_svn['svn_username']))
    config.append(('Production server', settings_samba['smb_server']))
    config.append(('Production username', settings_samba['smb_username']))
    # print config
    return config
