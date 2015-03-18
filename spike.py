#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# ygavrilenko@gmail.com

import svn
import filemanage
import conf
import sys
import argparse
from datetime import datetime
from encrypt_password import enc


def show_config():
    for item in conf.show_config():
        print ('%-20s:\t %s' % (item[0], item[1]))


def main():
    parser = argparse.ArgumentParser(prog='Automatic deploy')
    # parser.add_argument('show-config', help='Show current config')
    parser.add_argument('-s', '--show-config', action='store_true', help='show current config')
    parser.add_argument('-c', '--check-ticket', type=int, dest='bpms', help='checking for earlier deployment')
    parser.add_argument('-l', '--check-log', type=int, dest='rev', help='show svn log')
    parser.add_argument('-p', '--prepare', nargs=2, dest='id', action='append',
                        type=int, help='Prepare to deployment. Backup from production and export from svn.'
                                       ' First id=bpms, second id=svn revision ')
    parser.add_argument('-d', '--deploy', type=int, help='upload new revision from ticket to production')
    parser.add_argument('-r', '--rollback', type=int, help='Restore from backup current ticket')
    parser.add_argument('-e', '--encrypt', type=str, dest='password', help='Print encrypted password')

    args = vars(parser.parse_args())
    # print args
    if len(sys.argv) == 1:
        print parser.print_help()
    if args['show_config'] and args['rev'] is None and args['id'] is None and args['deploy'] is None \
            and args['rollback'] is None and args['bpms'] is None:
        show_config()
    if args['bpms'] > 0 and args['show_config'] is False and args['rev'] is None and args['id'] is None \
            and args['deploy'] is None and args['rollback'] is None:
        # print "[INFO]\t Create folder is not exist"
        filemanage.check_local_storage()
        result = filemanage.check_ticket(args['bpms'])
        if result[0] is True:
            print "[INFO]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tTicket not found on local storage"
    if args['rev'] > 0 and args['show_config'] is False and args['bpms'] is None and args['id'] is None \
            and args['deploy'] is None and args['rollback'] is None:
        print svn.svn_show_log(args['rev'], args['rev'])
    if args['id'] and args['show_config'] is False and args['rev'] is None \
            and args['deploy'] is None and args['rollback'] is None:
        filemanage.prepare_file_for_deployment(args['id'][0][0], args['id'][0][1])
    if args['deploy'] and args['show_config'] is False and args['rev'] is None \
            and args['id'] is None and args['rollback'] is None:
        result = filemanage.check_ticket(args['deploy'])
        if result[0] is False:
            filemanage.upload_file(args['deploy'])
        else:
            print "[WARN]\t"+datetime.now().strftime('%H:%M:%S %d-%m-%y')+"\tTicket not prepared to deploy"
    if args['rollback'] and args['show_config'] is False and args['rev'] is None \
            and args['id'] is None and args['deploy'] is None:
        filemanage.rollback(args['rollback'])
    if args['password'] and args['show_config'] is False and args['rev'] is None \
            and args['id'] is None and args['deploy'] is None and args['rollback'] is None:
        enc(args['password'])

    return 0


if __name__ == "__main__":
    main()