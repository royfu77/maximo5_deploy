#!/usr/bin/env python
# -*- coding: utf-8 -*-
#ygavrilenko@gmail.com

import os
import conf
from shutil import rmtree, copy2
from datetime import datetime
from hashlib import md5
import svn
from smb.SMBConnection import SMBConnection


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
    return main, samba

# this function copy-paste from source code pysmb/base/util/__init__
def convert_file_time_to_epoch(t):
    return (t - 116444736000000000L) / 10000000.0


# check local directory and create if not exist
def check_local_storage():
    main, s = set_samba_settings()
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
        return True, main["local_storage"]+delimiter()+str(ticket_id)
    else:
        #
        if not os.path.isdir(main["local_storage"]+delimiter()+str(ticket_id)):
            print "[WARN]\tPath "+str(main["local_storage"])+delimiter()+str(ticket_id)+" not directory, please check it"
            return False, None
        else:
            # print len(os.listdir(main["local_storage"]+delimiter()+str(ticket_id)+delimiter()))
            # print os.path.isfile(main["local_storage"]+delimiter()+str(ticket_id)+delimiter()+"notes.txt")
            if len(os.listdir(main["local_storage"]+delimiter()+str(ticket_id)+delimiter())) < 3 or os.path.isfile(main["local_storage"]+delimiter()+str(ticket_id)+delimiter()+"notes.txt") is False:
                print "[WARN]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tPath "+str(main["local_storage"]) + \
                      delimiter()+str(ticket_id) + \
                      " already exist, but directory is empty or deploy is not complited." \
                      "\n\t\tFlushing directory and reused it."
                rmtree(main["local_storage"]+delimiter()+str(ticket_id))
                return True, main["local_storage"]+delimiter()+str(ticket_id)
            with open(main["local_storage"]+delimiter()+str(ticket_id)+delimiter()+"notes.txt","r") as note:
                print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tTicket#"+str(ticket_id)+" was processed earlier."
                print note.read()
                return False, None


# backuping prod file
def get_production_backup(path, list_filename):
    main, samba = set_samba_settings()
    # FORCE umount all network drive
    os.system('net use * /delete /y')
    os.system('net use /persistent:no')
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


# new function for backup, worked via pysmb
def get_production_backup2(path, list_filename):
    main, samba = set_samba_settings()
    conn = SMBConnection(samba['smb_username'], samba['smb_password'], os.environ['COMPUTERNAME'], 'maximopreprod', use_ntlm_v2 = True)
    conn.connect(samba['smb_server'], 139)
    prod_files = filter(lambda x: x[7:17] == 'MAXIMOTEST' and x[18:25] != 'SOURCES' and x[18:24] != 'DB_OBJ', list_filename)
    file_info = {}
    for f in prod_files:
        # check directory exist on remote server
        rem_path = ('maximo/'+f[18:-len(os.path.basename(f))-1]).split('/')
        ch_path = ''
        dir_exist = True
        for item in rem_path:
            # print 'Item: '+item
            testdir = conn.listPath('c$', ch_path)
            if item == 'maximo':
                ch_path = ch_path+delimiter()+item
                continue
            if item in [x.filename for x in testdir]:
                pass
            else:
                dir_exist = False
                break
            ch_path = ch_path+delimiter()+item
        if dir_exist is False:
            continue
        # print f
        testfiles = conn.listPath('c$', 'maximo/'+f[18:-len(os.path.basename(f))])  # observe target directory
        if os.path.basename(f) in [x.filename for x in testfiles]:                  # check file exist on remote directory
            if not os.path.exists(path+delimiter()+f[:-len(os.path.basename(f))].replace('/', '\\')):
                os.makedirs(path+delimiter()+f[:-len(os.path.basename(f))].replace('/', '\\'))  # create backup dir
            with open(path+delimiter()+f.replace('/', '\\'), 'wb') as local_file:
                file_attributes, filesize = conn.retrieveFile('c$',
                                                                  delimiter()+'maximo'+delimiter()+f[18:].replace('/', '\\'),
                                                                  local_file)
            # file_time = conn.getAttributes('c$', 'maximo/'+f[18:])
            # os.utime(path+delimiter()+f.replace('/', '\\'), (os.stat(path+delimiter()+f.replace('/', '\\')).st_ctime, convert_file_time_to_epoch(file_time.last_write_time)))
            file_info[f] = []
            file_info[f].append(filesize)
            file_info[f].append(md5(open(path+delimiter()+f.replace('/', '\\'), 'rb').read()).hexdigest())
    conn.close()
    return file_info


# create local structure and load file from svn
def prepare_file_for_deployment(ticket_id, svn_id):
    status, path = check_ticket(ticket_id)
    if status is True:
        os.mkdir(path)
        os.mkdir(path+delimiter()+"for_deployment")
        os.mkdir(path+delimiter()+"backup")
        with open(path+delimiter()+'notes.txt', 'w') as f:
            f.write("-"*128+"\nDate:\t\t"+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\n")
            f.write("Ticket:\t\t"+str(ticket_id)+"\n")
            f.write("Revision:\t"+str(svn_id)+"\n")
            f.write("Deployer:\t"+str(username())+"\n")
            f.write("-"*56+" File for deploy"+"-"*56+"\n")
            f.write('%-75s\t%9s\t%32s\n%s\n' % ('Filename', 'Size(byte)', 'md5hash', '-'*128))
            print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tExport new files from svn"
            svn_file_info = svn.svn_export_files(svn_id, path+delimiter()+"for_deployment")
            list_filename = sorted(svn_file_info.keys())
            for filename in list_filename:
                f.write('%-75s\t%9s\t%32s\n' % (filename, svn_file_info[filename][0], svn_file_info[filename][1]))
            # backup_file = get_production_backup(path+delimiter()+"backup", list_filename)
            print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tBackup files from production"
            backup_file = get_production_backup2(path+delimiter()+"backup", list_filename)
            f.write("-"*57+" Backup  files"+"-"*57+"\n")
            for filename in sorted(backup_file.keys()):
                f.write('%-75s\t%9s\t%32s\n' % (filename, backup_file[filename][0], backup_file[filename][1]))

    return 0


# store new file on production server
def upload_file(ticket_id):
    main, samba = set_samba_settings()
    path = main['local_storage']+delimiter()+str(ticket_id)+delimiter()+'for_deployment'\
           + delimiter()+'trunk'+delimiter() + 'maximotest'
    tree = []
    for item in os.walk(path):
        item = (item[0].replace(path, ''), item[1], item[2])
        if item[0].replace(path, '')[1:8] == 'SOURCES':
            continue
        tree.append(item)
    conn = SMBConnection(samba['smb_username'], samba['smb_password'], os.environ['COMPUTERNAME'], 'maximopreprod', use_ntlm_v2 = True)
    conn.connect(samba['smb_server'], 139)
    # for test using c:\temp\maximo
    # loop in loop create file structure on remote server, copy file and writing action_log
    action_log = []
    notes = open(main['local_storage']+delimiter()+str(ticket_id)+delimiter()+'notes.txt', 'a+')
    notes.write("-"*57+"Uploaded files"+"-"*57+"\n")
    notes.write('%-75s\t%9s\t%s\n%s\n' % ('Remote filename', 'Size(byte)', 'Timestamp', '-'*128))
    for i in tree:
        for k in i[1]:
            if k == 'SOURCES' or k == 'DB_OBJ': continue
            if k not in [x.filename for x in conn.listPath('c$', 'maximo'+i[0])]:
                # for testing using path temp/maximo for prod need remote temp
                ch_path = 'maximo'+i[0]+delimiter()+str(k)
                conn.createDirectory('c$', ch_path)
                print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tCreate directory "+\
                      delimiter()+delimiter()+samba['smb_server']+delimiter()+"c$"+delimiter()+ch_path
                action_log.append(('mkdir', delimiter()+delimiter()+samba['smb_server']+delimiter()+'c$'+delimiter()+ch_path))
        if len(i[2]) > 0 and 'DB_OBJ' != i[0][1:]:
            for f in i[2]:
                f_path = 'maximo'+i[0]+delimiter()
                obj_file = str(path)+str(i[0])+delimiter()+str(f)
                file_size = conn.storeFile('c$', f_path+f, open(obj_file, 'rb'))
                notes.write('%-75s\t%9s\t%s\n' % (delimiter()+delimiter()+samba['smb_server']+delimiter()+"c$"+delimiter()+f_path+f, str(file_size), datetime.now().strftime('%Y-%d-%m %H:%M:%S')))
                print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tUploaded size in byte:"+str(file_size)+\
                      ", file: "+delimiter()+delimiter()+samba['smb_server']+delimiter()+"c$"+delimiter()+f_path+f
                action_log.append(('cp', delimiter()+delimiter()+samba['smb_server']+delimiter()+'c$'+delimiter()+f_path+f))
    # write rollback file
    with open((main['local_storage']+delimiter()+str(ticket_id)+delimiter()+'action.log'), 'w') as rollback:
        for line in action_log:
            rollback.write(line[0]+','+line[1]+'\n')
    conn.close()
    notes.close()
    return 0


# remove new files and restore from backup
def rollback(ticket_id):
    main, samba = set_samba_settings()
    conn = SMBConnection(samba['smb_username'], samba['smb_password'], os.environ['COMPUTERNAME'], 'maximopreprod', use_ntlm_v2 = True)
    conn.connect(samba['smb_server'], 139)
    action_log = []
    with open((main['local_storage']+delimiter()+str(ticket_id)+delimiter()+'action.log'), 'r') as log:
        for line in log.readlines():
            action_log.append(line.strip())
    action_log.reverse()
    notes = open(main['local_storage']+delimiter()+str(ticket_id)+delimiter()+'notes.txt', 'a+')
    notes.write("-"*54+" Rollback all change"+"-"*54+"\n")
    notes.write('%-75s\t%9s\t%s\n%s\n' % ('Remote filename', 'Action', 'Timestamp', '-'*128))
    for line in action_log:
        line = line.split(',')
        # generate path for smb
        path = '\\'.join(line[1][2:].split('\\')[2:])
        if line[0] == 'cp':
            conn.deleteFiles('c$', path)
            print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tFile deleted: "+line[1]
        if line[0] == 'mkdir':
            conn.deleteDirectory('c$', path)
            print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tDirectory deleted: "+line[1]
        notes.write('%-75s\t%9s\t%s\n' % (line[1], 'Deleted', datetime.now().strftime('%Y-%d-%m %H:%M:%S')))
    os.remove(main['local_storage']+delimiter()+str(ticket_id)+delimiter()+'action.log')
    path = main['local_storage']+delimiter()+str(ticket_id)+delimiter()+'backup'\
           + delimiter()+'trunk'+delimiter() + 'maximotest'
    tree = []
    for item in os.walk(path):
        item = (item[0].replace(path, ''), item[1], item[2])
        if item[0].replace(path, '')[1:8] == 'SOURCES':
            continue
        tree.append(item)
    for item in tree:
        if len(item[2]) > 0:
            for f in item[2]:
                f_path = 'maximo'+item[0]+delimiter()
                obj_file = str(path)+str(item[0])+delimiter()+str(f)
                file_size = conn.storeFile('c$', f_path+f, open(obj_file, 'rb'))
                file_path = delimiter()+delimiter()+str(samba['smb_server'])+delimiter()+"c$"+delimiter()+f_path+f
                print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tFile restored from backup: "+str(file_path)
                notes.write('%-75s\t%9s\t%s\n' % (file_path, 'Restored', datetime.now().strftime('%Y-%d-%m %H:%M:%S')))

    conn.close()
    return 0


# prepare_file_for_deployment(1615344, 5393)
# upload_file(1604065)
# rollback(1604065)