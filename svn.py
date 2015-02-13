#!/usr/bin/env python
# -*- coding: utf-8 -*-
#ygavrilenko@gmail.com

import pysvn
import conf
import datetime

#get settings from config.ini
def set_svn_settings():
    m,svn, s = conf.load_config()
    client = pysvn.Client()
    client.set_default_username(svn['svn_username'])
    client.set_default_password(svn['svn_password'])
    url = svn['repository']
    return client, url


#return log for revision or range of revisions
def svn_show_log(start_id, end_id):
    client, url = set_svn_settings()
    result=""
    for count in range(0,(end_id-start_id)+1):
        revision_number=str(client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("revision"))[22:-1]
        revision_message=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("message")
        revision_date=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("date")
        revision_date=datetime.datetime.fromtimestamp(int(revision_date)).strftime('%Y-%m-%d %H:%M:%S')
        revision_author=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("author")
        qty_file=len(client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths"))
        result+="#"*80+"\n  Rev:\t\t\t"+revision_number+"\n  Author:\t\t"+revision_author+"\n  Comments:\t\t"+revision_message+"\n  Commit date:\t"+revision_date+"\n  Total object:\t"+str(qty_file)+"\n"
        for file in range(0,qty_file):
            f_name=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths")[file]['path']
            f_status=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths")[file]['action']
            result+="\t"+f_status+" "+f_name+"\n"
    return result





#a=svn_show_log(5323,5323)
#print a
