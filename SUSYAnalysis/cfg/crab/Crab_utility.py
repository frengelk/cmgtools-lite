#!/usr/bin/env python

import sys,os, re, pprint
import re
import argparse

cmssw_release = os.environ['CMSSW_BASE']
user = os.environ['USER']

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Crab utility', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--resubmit', action='store_true')#, help='if resubmit', metavar='resubmit')
    parser.add_argument('--status',  action='store_true')
    parser.add_argument('--getoutput',  action='store_true')
    parser.add_argument('--kill',  action='store_true')

    args = parser.parse_args()
    re = args.resubmit
    stat = args.status
    getout = args.getoutput
    kill = args.kill

    top = os.getcwd()
    print("issue a crab --command  for all crab dirs in this dir {}".format(top))
    for root, dirs, files in os.walk(top):
        for crab_dir in dirs:
            if "crab" in crab_dir:
                for root_2, dirs_2, files_2 in os.walk(crab_dir):
                    for sub_dir in dirs_2:
                        if "crab" in sub_dir:
                            if re:
                                print("\n")#for {0}/{1}".format(crab_dir, sub_dir))
                                print("crab resubmit {0}/{1}".format(crab_dir, sub_dir))
                                os.system("crab resubmit {0}/{1}".format(crab_dir, sub_dir))
                            elif stat:
                                print("crab stat {0}/{1}".format(crab_dir, sub_dir))
                                os.system("crab status {0}/{1}".format(crab_dir, sub_dir))
                            elif getout:
                                print("crab getoutput {0}/{1}".format(crab_dir, sub_dir))
                                os.system("crab getoutput {0}/{1}".format(crab_dir, sub_dir))
                            elif kill:
                                print("crab kill {0}/{1}".format(crab_dir, sub_dir))
                                os.system("crab kill {0}/{1}".format(crab_dir, sub_dir))
                            else:
                                print("you ok? Do something")
