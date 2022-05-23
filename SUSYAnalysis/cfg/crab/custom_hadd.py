#!/usr/bin/env python

import sys,os, re, pprint
import re
import argparse
#import ROOT

cmssw_release = os.environ['CMSSW_BASE']
user = os.environ['USER']

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Hadd for crab output', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--indir', help='Give it the crab/.../results', metavar='indir')
        parser.add_argument('--outdir', help='output directory', metavar='outdir')
        parser.add_argument('--hadd_name', metavar='hadd_name')

        args = parser.parse_args()
        indir = args.indir
        outdir = args.outdir
        hadd_name = args.hadd_name

        if not os.path.exists(outdir):
            print("creating {}".format(outdir))
            os.system("mkdir {}".format(outdir))

            for root, dirs, files in os.walk(indir):
                #print("untaring files:", files)
                # rename it to chunks so heppy_hadd works
                for file in files:
                    os.system("tar -xf {0}/{1} -C {2}".format(indir, file, outdir))
                    #from IPython import embed;embed()
                    # declare new dir name to chunk
                    process = indir.split("/")[0].split("_")[2:-3]
                    process.extend(["chunk", file.replace(".tgz","").split("_")[1]])
                    name = "_".join(process)
                    os.system("mv {0}/Output {0}/{1}".format(outdir, name))

                #from IPython import embed; embed()

            #os.system("rm -r {}/Output".format(outdir))
            print("finished untaring")

        else:
            print("Assuming the outdir is complete")

        #from IPython import embed; embed()
        hadd_files = ""
        for root, dirs, files in os.walk(outdir):

            for hep_dir in dirs:
                hadd_files += "{0}/{1}/treeProducerSusySingleLepton/tree.root ".format(outdir, hep_dir)

            #print("hadding to {0}/{1} from {2}".format(outdir, hadd_name, hadd_files))
            #os.system("hadd -f {0}/{1} {2}".format(outdir, hadd_name, hadd_files))
            break # just loop at top level
