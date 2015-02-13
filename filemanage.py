#!/usr/bin/env python
# -*- coding: utf-8 -*-
#ygavrilenko@gmail.com

import os
import conf
from shutil import rmtree

def delimiter():
    if os.name=='nt':
        return '\\'
    else:
        return '/'

#return tuple of dict with setting
def set_samba_settings():
    main, s, samba = conf.load_config()
    return main,samba

#check local directory and create if not exist
def check_local_storage():
    main,s = set_samba_settings()
    if not os.path.exists(main["local_storage"]):
        os.makedirs(main["local_storage"])
    else:
        if not os.path.isdir(main["local_storage"]):
            print "[WARN]\tPath "+str(main["local_storage"])+" not directory, please check it"
    if not os.path.exists(main["log_dir"]):
        os.makedirs(main["log_dir"])
    else:
        if not os.path.isdir(main["log_dir"]):
            print "[WARN]\tPath "+str(main["log_dir"])+" not directory, please check it"

#returm tuple(True/False, path)
def check_ticket(ticket_id):
    main,s = set_samba_settings()
    #if directory with ticket number not exist return true
    if not os.path.exists(main["local_storage"]+delimiter()+str(ticket_id)):
        print "Ticket "+str(ticket_id)+" was not processed earlier"
        return True, main["local_storage"]+delimiter()+str(ticket_id)
    else:
        #
        if not os.path.isdir(main["local_storage"]+delimiter()+str(ticket_id)):
            print "[WARN]\tPath "+str(main["local_storage"])+delimiter()+str(ticket_id)+" not directory, please check it"
            return False, None
        else:
            if len(os.listdir(main["local_storage"]+delimiter()+str(ticket_id)+delimiter())) < 3 or os.path.isfile(main["local_storage"]+delimiter()+str(ticket_id)+delimiter()+"notes.txt") is False:
                print "[WARN]\tPath "+str(main["local_storage"])+delimiter()+str(ticket_id)+" already exist, but directory is empty or deploy is not complited.\n\t\tFlushing directory and reused it."
                rmtree(main["local_storage"]+delimiter()+str(ticket_id))
                return True, main["local_storage"]+delimiter()+str(ticket_id)
            with open(main["local_storage"]+delimiter()+str(ticket_id)+delimiter()+"notes.txt","r") as note:
                print "Ticket#"+str(ticket_id)+" was processed earlier.\nNotes:"
                print note.read()
                return False, None

#create local structure and load file from svn
def prepare_file_for_deployment(ticket_id, svn_id):
    status, path = check_ticket(ticket_id)
    #print status, path
    if status is True:
        os.mkdir(path)
        os.mkdir(path+delimiter()+"for_deployment")
        os.mkdir(path+delimiter()+"backup")
        #print os.listdir(path)


prepare_file_for_deployment(1232312,2323)
