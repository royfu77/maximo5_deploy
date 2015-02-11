#!/usr/bin/env python
# -*- coding: utf-8 -*-
#ygavrilenko@gmail.com

import pysvn
import conf


def set_svn_settings():
    m, svn = conf.load_config()
    client = pysvn.Client()
    client.set_default_username(svn['svn_username'])
    client.set_default_password(svn['svn_password'])
    url = svn['repository']
    return client, url


def svn_show_log(start_id, end_id):
    client, url = set_svn_settings()
    for count in range(0,(end_id-start_id)+1):
        revision_number=str(client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("revision"))[22:-1]
        revision_message=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("message")
        qty_file=len(client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths"))
        print "#"*80+"\n  Rev:\t\t\t"+revision_number+"\n  Comments:\t\t"+revision_message+"\n  Total files:\t"+str(qty_file)
        for file in range(0,qty_file):
            f_name=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths")[file]['path']
            f_status=client.log(url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,start_id ),
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,end_id),
                             discover_changed_paths=True,limit=0)[count].get("changed_paths")[file]['action']
            print "\t"+f_status+" "+f_name





svn_show_log(5012, 5014)
"""
client,url=set_svn_settings()
print client.log( url,revision_start=pysvn.Revision( pysvn.opt_revision_kind.number,2180 ),revision_end=pysvn.Revision( pysvn.opt_revision_kind.number,2180),discover_changed_paths=True,limit=0)[0].get("changed_paths")[0]['path']
"""