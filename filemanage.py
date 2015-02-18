#!/usr/bin/env python
# -*- coding: utf-8 -*-
#ygavrilenko@gmail.com

import os
import conf
from shutil import rmtree, copy2
from datetime import datetime
from hashlib import md5
import svn


def delimiter():
    if os.name == 'nt':
        return '\\'
    else:
        return '/'


def username():
    if os.name == 'nt':
        return os.environ['USERNAME']
    else:
        return os.environ['USER']


# return tuple of dict with setting
def set_samba_settings():
    main, s, samba = conf.load_config()
    return main,samba


# check local directory and create if not exist
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


# return tuple(True/False, path)
def check_ticket(ticket_id):
    main, s = set_samba_settings()
    # if directory with ticket number not exist return true
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
                print "[WARN]\tPath "+str(main["local_storage"]) + \
                      delimiter()+str(ticket_id) + \
                      " already exist, but directory is empty or deploy is not complited." \
                      "\n\t\tFlushing directory and reused it."
                rmtree(main["local_storage"]+delimiter()+str(ticket_id))
                return True, main["local_storage"]+delimiter()+str(ticket_id)
            with open(main["local_storage"]+delimiter()+str(ticket_id)+delimiter()+"notes.txt","r") as note:
                print "Ticket#"+str(ticket_id)+" was processed earlier."
                print note.read()
                return False, None


# backuping prod file
def get_production_backup(path, list_filename):
    main, samba = set_samba_settings()
    # connect temp disk B:
    command = 'net use b: \\\\'+samba['smb_server']+"\\c$\MAXIMO /user:"+samba['smb_username']+' "'+samba['smb_password']+'"'
    os.system(command)
    file_info = {}  # dictionary with backup file  meta data
    for file in list_filename:
        if file[7:17] == 'MAXIMOTEST' and file[18:25] != 'SOURCES' and file[18:24] != 'DB_OBJ':
            # create destination directory and backup files if it exists in source
            if os.path.exists('b:'+delimiter()+file[18:].replace('/', '\\')):
                if not os.path.isdir(path+file[:-len(os.path.basename(file))].replace('/', '\\')):
                    os.makedirs(path+file[:-len(os.path.basename(file))].replace('/', '\\'))
                copy2('b:'+delimiter()+file[18:].replace('/', '\\'), path+file[:-len(os.path.basename(file))].replace('/', '\\'))
                file_info[file] = []
                file_info[file].append(int(os.path.getsize(path+file[:-len(os.path.basename(file))].replace('/', '\\')+os.path.basename(file))))
                file_info[file].append(md5(open(path+file[:-len(os.path.basename(file))].replace('/', '\\')+os.path.basename(file), 'rb').read()).hexdigest())
    os.system('net use b: /delete')
    return file_info


# create local structure and load file from svn
def prepare_file_for_deployment(ticket_id, svn_id):
    status, path = check_ticket(ticket_id)
    if status is True:
        os.mkdir(path)
        os.mkdir(path+delimiter()+"for_deployment")
        os.mkdir(path+delimiter()+"backup")
        with open(path+delimiter()+'notes.txt', 'w') as f:
            f.write("Date:\t\t"+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\n")
            f.write("Ticket:\t\t"+str(svn_id)+"\n")
            f.write("Deployer:\t"+str(username())+"\n")
            f.write("-"*50+" File for deploy"+"-"*50+"\n")
            f.write('%-70s\t%9s\t%32s\n%s\n' % ('Filename', 'Size(byte)', 'md5hash', '-'*116))
            svn_file_info = svn.svn_export_files(svn_id, path+delimiter()+"for_deployment")
            list_filename = sorted(svn_file_info.keys())
            for filename in list_filename:
                f.write('%-70s\t%9s\t%32s\n' % (filename, svn_file_info[filename][0], svn_file_info[filename][1]))
            backup_file = get_production_backup(path+delimiter()+"backup", list_filename)
            f.write("-"*50+" Backup  files "+"-"*50+"\n")
            for filename in sorted(backup_file.keys()):
                f.write('%-70s\t%9s\t%32s\n' % (filename, svn_file_info[filename][0], svn_file_info[filename][1]))

    return 0

"""
get_production_backup('d:\\tmp\\bpms\\', ['/trunk/MAXIMOTEST/custom/app/rtt/mbo/RTTDocsMbo.class',
                                          '/trunk/MAXSAP/custom/app/rtt/mbo/RTTDocsMbo.class',
                                          '/trunk/MAXIMOTEST/psdi/jsp/app/wotrack/ActionsWO.class',
                                          '/trunk/MAXIMOTEST/SOURCES/custom/app/rtt/mbo/RTTDocsMbo.java',
                                          '/trunk/DB_OBJ/VIEW.test.sql'])
"""
prepare_file_for_deployment(1632111, 5385)
