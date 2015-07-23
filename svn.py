#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ygavrilenko@gmail.com

import pysvn
import conf
import datetime
import os
from hashlib import md5


# get settings from config.ini
def set_svn_settings():
    m, svn, s = conf.load_config()
    client = pysvn.Client()
    client.set_default_username(svn['svn_username'])
    client.set_default_password(svn['svn_password'])
    url = svn['repository']
    return client, url


# return log for revision or range of revisions
def svn_show_log(start_id, end_id):
    client, url = set_svn_settings()
    result = ""
    for count in range(0, (end_id-start_id)+1):
        revision_number = str(client.log(url, revision_start=pysvn.Revision( pysvn.opt_revision_kind.number, start_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number ,end_id),
                             discover_changed_paths=True, limit=0)[count].get("revision"))[22:-1]
        revision_message = client.log(url, revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, start_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, end_id),
                             discover_changed_paths=True, limit=0)[count].get("message")
        revision_date = client.log(url, revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, start_id),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number, end_id),
                             discover_changed_paths=True, limit=0)[count].get("date")
        revision_date = datetime.datetime.fromtimestamp(int(revision_date)).strftime('%Y-%m-%d %H:%M:%S')
        revision_author = client.log(url,revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, start_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, end_id),
                             discover_changed_paths=True,limit=0)[count].get("author")
        qty_file = len(client.log(url, revision_start=pysvn.Revision( pysvn.opt_revision_kind.number, start_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, end_id),
                             discover_changed_paths=True, limit=0)[count].get("changed_paths"))
        result += ("%s\nRev:\t\t %-20s\nAuthor:\t\t %-20s\nComments:\t %-20s\nCommit Date:\t %-20s\nTotal object:\t %-20s\n" %
                   ("-"*120, revision_number, revision_author, revision_message, revision_date, str(qty_file)))
        for file in range(0, qty_file):
            f_name = client.log(url, revision_start=pysvn.Revision( pysvn.opt_revision_kind.number, start_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths")[file]['path']
            f_status = client.log(url,revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, start_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths")[file]['action']
            result += "\t"+f_status+" "+f_name+"\n"
    return result


# export file by svn and return dictionary[filename]= [hashsum, size]
def svn_export_files(svn_id, path):
    client, url = set_svn_settings()
    qty_file = len(client.log(url, revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, svn_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, svn_id),
                             discover_changed_paths=True, limit=0)[0].get("changed_paths"))
    raw_files = []
    for file in range(0, qty_file):
        status = client.log(url, revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, svn_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, svn_id),
                             discover_changed_paths=True, limit=0)[0].get("changed_paths")[file]['action']
        if status == 'D':       # if object marked deleted, skip it
            continue
        raw_files.append(client.log(url, revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, svn_id),
                             revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, svn_id),
                             discover_changed_paths=True, limit=0)[0].get("changed_paths")[file]['path'])
    dirs = sorted(set(os.path.dirname(dir) for dir in raw_files))  # set with only directory's
    files = [i for i in raw_files if len(os.path.basename(i).split('.')) >= 2]  # list with only files
    [os.makedirs(path+directory) for directory in dirs]  # create directory tree
    file_info = {}  # dictionary with new file  meta data
    for file in files:
        client.export(url+file, path+file, peg_revision=pysvn.Revision(pysvn. opt_revision_kind.number, svn_id),
                      force=True, recurse=False)
        file_info[file] = []
        file_info[file].append(int(os.path.getsize(path+file)))
        file_info[file].append(md5(open(path+file, 'rb').read()).hexdigest())

    return file_info
