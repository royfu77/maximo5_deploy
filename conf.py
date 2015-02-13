#!/usr/bin/env python
#  -*- coding: utf-8 -*- 
#ygavrilenko@gmail.com



import ConfigParser
import os.path

def check_config():
    if os.path.isfile('./config.ini'):
        return True
#    print "[Error]\t\tconfig.ini not found in current directory"
    return False

def load_config():
#load and parse config, return list of dictionary
    settings_main,settings_svn,settings_samba={},{},{}
    config=ConfigParser.ConfigParser()
    config.read('config.ini')
    settings_main["local_storage"]=config.get("main","local_storage")
    settings_main["log_dir"]=config.get("main","log_dir")
    settings_svn["repository"]=config.get("repository","svn_url")
    settings_svn["svn_username"]=config.get("repository","svn_username")
    settings_svn["svn_password"]=config.get("repository","svn_password")
    settings_samba["smb_server"]=config.get("samba","smb_server")
    settings_samba["smb_username"]=config.get("samba","smb_username")
    settings_samba["smb_password"]=config.get("samba","smb_password")

    return settings_main,settings_svn,settings_samba

