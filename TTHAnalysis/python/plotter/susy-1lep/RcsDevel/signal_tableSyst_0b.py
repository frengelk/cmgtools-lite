#!/usr/bin/env python

import sys,os
import glob

#from makeYieldPlots import *
from makeYieldTables_0b import *
#from yieldClass import *

def PrintSignalSystematics(yds, header_names,dirName , file_name, var, systs, mGo, mLSP):

    samps = [("T5qqqqWW_Scan_{}_syst_mGo{}_mLSP{}".format(syst,mGo,mLSP),b)
            for syst in systs
            for b in bindirs
            if mGo >= mLSP
            ]

    yds = yds.getMixDict(samps)

    f =  open(dirName + "/" + file_name + "mGo{}_mLSP{}.dat".format(mGo, mLSP),'w')
    print "Writing systematics for", dirName + "/" + file_name + "mGo{}_mLSP{}.dat".format(mGo, mLSP)
    bins = sorted(yds.keys())
    precision = 5  # |  SBin
    f.write('bin                 |' +  ' %s ' % '     |   '.join(map(str, header_names)) + ' \n')
    for i,bin in enumerate(bins):
        bin_yds = [i for i in yds[bin] if i != 0]
        vals = [v
            for v in bin_yds
            if v.name.endswith("mGo{}_mLSP{}".format(mGo, mLSP))
            ]
        f.write(bin + '')
        for i,yd in enumerate(vals):

            if yd ==0:
                val=0
            else:
                val = abs(yd.val)
            f.write(('  |    %.'+str(precision)+'f   ' ) % (1+val))
        f.write('\n')
    f.close()
    return 1


if __name__ == "__main__":

    ## remove '-b' option

    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print '# pattern is', pattern
    else:
        print "No pattern given!"
        exit(0)

    #BinMask LTX_HTX_NBX_NJX for canvas names
    basename = os.path.basename('Syst')
    mask = basename.replace("*","X_")
    #year = pattern.split("_")[-1]
    if "run2" in pattern:
        year = "run2"
    elif "2016" in pattern:
        year = "2016"
    elif "2017" in pattern:
        year = "2017"
    elif "2018" in pattern:
        year = "2018"

    #dirName = "signal_syst_tables_new_{}".format(year)
    dirName = "signal_syst_tables_proper_{}".format(year)
    if '--test' in sys.argv:
        dirName = "signal_syst_tables_proper_dilep_{}".format(year)
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ")
    else:
        print("Directory " , dirName ,  " already exists")

    # Define storage
    yds = YieldStore("lepYields")
    ydsMu = YieldStore("muYields")

    if '--test' in sys.argv:
        dirName = "signal_syst_tables_proper_dilep_{}".format(year)
        yds.addFromFiles( "yield_0b_postmerge_" + year + "_prepSyst/signal_*/merged/LT1_HT0_NB0_NJ5_NW0*", ("lep","sele"))
        ydsMu.addFromFiles( "yield_0b_postmerge_" + year + "_prepSyst/signal_*/merged/LT1_HT0_NB0_NJ5_NW0*", ("mu","sele"))
    else:
        yds.addFromFiles( "yield_0b_postmerge_" + year + "_prepSyst/signal_*/merged/LT*", ("lep","sele"))
        ydsMu.addFromFiles( "yield_0b_postmerge_" + year + "_prepSyst/signal_*/merged/LT*", ("mu","sele"))

    systs = glob.glob('{}/signal_*'.format(pattern))
    systs = [syst[syst.find('signal_')+7:] for syst in systs]
    systsprint = systs

    var = "T5qqqqWW_Scan"
    bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB', "SR_SB_NB1i", "CR_SB_NB1i", "SR_SB_NB0", "CR_SB_NB0"]

    print "Writing files in", dirName

    caption = 'Zero-b analysis: Systematic uncertainties on Signal for different sources {}'.format(year)

    massDf = read_csv("massFile.md")
    MGO = massDf["mGo"].values
    MLSP = massDf["mLSP"].values

    header_names = [b+"_"+syst
                   for syst in systsprint
                   for b in bindirs]

    for mGo, mLSP in zip(MGO, MLSP):
        PrintSignalSystematics(yds, header_names, dirName, 'signalTablev1_{}_'.format(year), var, systs, mGo, mLSP)
        PrintSignalSystematics(ydsMu, header_names, dirName, 'signalTablev1_Mu_{}_'.format(year), var, systs, mGo, mLSP)
