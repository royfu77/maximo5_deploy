#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# ygavrilenko@gmail.com

import svn
import filemanage
import conf
import sys
import argparse


def show_config():
    for item in conf.show_config():
        print ('%-20s:\t %s' % (item[0], item[1]))


def main():
    parser = argparse.ArgumentParser(prog='Automatic deploy')
    # parser.add_argument('show-config', help='Show current config')
    parser.add_argument('-s', '--show-config', action='store_true', help='show current config')
    parser.add_argument('-c', '--check-ticket', type=int, dest='bpms', help='checking for earlier deployment')
    parser.add_argument('-l', '--check-svn-log', type=int, dest='rev', help='show svn log')
    parser.add_argument('-p', '--prepare', nargs=2, dest='id', action='append',
                        type=int, help='Prepare to deployment. Backup from production and export from svn.'
                                       ' First id=bpms, second id=svn revision ')
    parser.add_argument('-d', '--deploy', nargs=1, type=int, dest='bpms', help='upload new revision from ticket to production')
    parser.add_argument('-r', '--rollback', nargs=1, type=int, dest='bpms', help='Restore from backup current ticket')

    args = vars(parser.parse_args())
    print args
    if len(sys.argv) == 1:
        print parser.print_help()
    if args['show_config'] is True and args['bpms'] is None and args['rev'] is None and args['id'] is None:
        show_config()
    else:
        print "Option -s/--show-config not use with other option"
    return 0


if __name__ == "__main__":
    main()