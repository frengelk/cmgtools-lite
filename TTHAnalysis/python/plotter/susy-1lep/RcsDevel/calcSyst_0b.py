#!/usr/bin/env python

#import numpy as np
import glob, os, sys, math
from math import hypot
from ROOT import *

from readYields import getYield


def getDirNames(fname):

    tfile = TFile(fname,"READ")

    dirList = [dirKey.ReadObj().GetName() for dirKey in gDirectory.GetListOfKeys() if dirKey.IsFolder() == 1]

    tfile.Close()

    return dirList

def getHnames(fname,tdir):

    tfile = TFile(fname,"READ")
    tfile.cd(tdir)

    hnames = []

    for key in gDirectory.GetListOfKeys():

        obj = key.ReadObj()
        hnames.append(obj.GetName())

    tfile.Close()

    return hnames

def GetUpDownList(fname):

    tfile = TFile(fname,"READ")

    uplist = []
    downlist = []

    for k in tfile.GetListOfKeys():
        histname=k.ReadObj().GetName()
        if "Up" in histname:
            uplist.append(histname)
        if "Down" in histname:
            downlist.append(histname)

    return uplist,downlist

def getSystHist(tfile, hname, syst = "Xsec"):
    if "Env" in syst or "RMS" in syst:
        print("why are you here?")
        return 0
    else:

        upName = hname + '_' + syst + '-Up'
        dnName = hname + '_' + syst + '-Down'

        #print upName
        hNorm = tfile.Get(hname)
        hUp = tfile.Get(upName)
        hDown = tfile.Get(dnName)

        hSyst = hUp.Clone(hNorm.GetName() + '_' + syst + '_syst')
        hSyst.Add(hDown, -1)
        hSyst.Divide(hNorm)
        hSyst.Scale(0.5)

        #xBin = hSyst.GetXaxis().GetBinCenter(225)
        #yBin = hSyst.GetYaxis().GetBinCenter(225)
        #print xBin, "/", hSyst.GetXaxis().GetNbins(), yBin,"/", hSyst.GetXaxis().GetNbins(), ":", hSyst.GetBinContent(xBin, yBin)

        return (hSyst,hUp,hDown)


def makeSystHists(fileList): #direc,
    print "Making syst hists"
    if 'signal_' in path:
        hnames = ["T5qqqqWW_Scan"] # process name
    else:
        hnames = ['EWK', 'DY', 'QCD', 'SingleT', 'TTJets', 'TTV', 'VV', 'WJets', 'other_bkg']

    # systematic alawys first subdirectory
    print "path =", path
    print path.split("/")
    if "run2" in path:
        systNames = [path.split("/")[1].split("_")[1] + "_" + path.split("/")[1].split("_")[2]]
    else:
        systNames = [path.split("/")[1].split("_")[1]]
    print hnames, systNames

    #bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB']
    #bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB','Kappa','Rcs_MB','Rcs_SB']

    #from IPython import embed;embed()

    #bindirs = []
    bindirs = getDirNames(fileList[0])
    print("Found those dirs:", bindirs)
    bindirs = [bin for bin in bindirs if "DL" not in bin]
    if 'signal_' in path:
        bindirs = ['SR_MB', 'CR_MB', 'SR_SB', 'CR_SB', 'SR_SB_NB0', 'CR_SB_NB0', 'SR_SB_NB1i', 'CR_SB_NB1i']
    else:
        bindirs = ['KappaTT', 'KappaB', 'KappaBTT', 'KappaW', 'SR_MB', 'CR_MB', 'SR_SB', 'CR_SB', 'SR_SB_NB0', 'CR_SB_NB0', 'SR_SB_NB1i', 'CR_SB_NB1i']
        #bindirs = ['KappaTT', 'KappaB', 'KappaBTT', 'KappaW']
    print bindirs

    #uplist, downlist = GetUpDownList(fileList[0])
    #print(uplist, downlist)
    # dir to store
    sysdir =  "syst/" #direc +
    if not os.path.exists(sysdir): os.makedirs(sysdir)

    #from IPython import embed;embed()

    for fname in fileList:
        tfile = TFile(fname,"UPDATE")

        for bindir in bindirs:
            if "syst" in path:
                if "KappaW" in bindir:
                    hnames = ['WJets']
                elif "Kappa" in bindir:
                    hnames = ['TTJets']
                else:
                    hnames = ['EWK', 'DY', 'QCD', 'SingleT', 'TTV', 'VV', 'other_bkg']
            elif "signal" in path:
                hnames = ["T5qqqqWW_Scan"] # process name
            else:
                print "Something is weird.. Check your path!:\n", path
                exit()

            for hname in hnames:
                for syst in systNames:
                    if bindir != "":
                        (hSyst,hUp,hDown) = getSystHist(tfile, bindir+'/'+ hname, syst)
                    else:
                        (hSyst,hUp,hDown) = getSystHist(tfile, hname, syst)

                    if (hSyst,hUp,hDown) == (1,2,3):
                        # this is a kinda hacky way, but it doesn't take to long. If performance is an issue, look here
                        # only the working systematics get included, the rest is passed
                        # so KappaTT for TTJets is working, but all other processes are skipped
                        # Advantage: generalizes the processing, don't have to check for working configurations
                        continue
                    if hSyst:
                        tfile.cd(bindir)
                        hSyst.Write("",TObject.kOverwrite)

        tfile.Close()
        #from IPython import embed;embed()
    return 1

def combineOtherBkgs(fileList):
    # hardcode MC hists to avoid kappa or repition errors
    bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB', "SR_SB_NB1i", "CR_SB_NB1i", "SR_SB_NB0", "CR_SB_NB0"]
    other_bkgs = ["DY", "SingleT", "TTV", "VV"]
    print "Combining other backgrounds"

    for fname in fileList:
        tfile = TFile(fname,"UPDATE")
        for bind in bindirs:
            # start with EWK always, so we have a tObject to add onto

            #systNames = [path.split("/")[1].split("_")[1] + "_" + path.split("/")[1].split("_")[2]]

            if "run2" in path:
                systNames = [path.split("/")[1].split("_")[1] + "_" + path.split("/")[1].split("_")[2]]
            else:
                systNames = [path.split("/")[1].split("_")[1]]

            #assert len(systNames)==1
            DY_nom = tfile.Get(bind+"/DY").Clone()
            DY_systUp = tfile.Get(bind+"/DY_"+systNames[0]+"-Up").Clone()
            DY_systDown = tfile.Get(bind+"/DY_"+systNames[0]+"-Down").Clone()
            for other in other_bkgs[1:]:
                otherNominal = tfile.Get(bind+"/{}".format(other)).Clone()
                other_systUp = tfile.Get(bind+"/{}_{}-Up".format(other,systNames[0])).Clone()
                other_systDown = tfile.Get(bind+"/{}_{}-Down".format(other,systNames[0])).Clone()
                #from IPython import embed; embed()
                DY_nom.Add(otherNominal)
                DY_systUp.Add(other_systUp)
                DY_systDown.Add(other_systDown)

            tfile.cd(bind)
            DY_systUp.SetName("other_bkg")
            DY_systUp.Write("",TObject.kOverwrite)
            tfile.cd(bind)
            DY_systUp.SetName("other_bkg_{}-Up".format(systNames[0]))
            DY_systUp.Write("",TObject.kOverwrite)
            tfile.cd(bind)
            DY_systDown.SetName("other_bkg_{}-Down".format(systNames[0]))
            DY_systDown.Write("",TObject.kOverwrite)
        tfile.Close()
    return 1


if __name__ == "__main__":

    ## remove '-b' option
    _batchMode = False

    if '-b' in sys.argv:
        sys.argv.remove('-b')
        _batchMode = True

    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        pattern = pattern.replace("//", "/")
        print('# pattern is', pattern)
    else:
        print("No pattern given!")
        exit(0)

    # find files matching pattern
    fList = glob.glob(pattern+"*.root")

    for root, dirs, files in os.walk(pattern):

        #print(root, dirs)
        for direc in dirs:
            if "signal" in direc or "syst" in direc:
                path = pattern +"/"+ direc
                for ro,di,fi in os.walk(path):
                    for d in di:
                        if "merged" == d:
                            fileList=[]
                            path = path +"/"+ d
                            print("doing systs for:",path)
                            for r,d,f in os.walk(path):
                                for file in f:
                                    if ".root" in file:
                                        fileList.append(path+"/"+file)

                            if "syst" in direc:
                                combineOtherBkgs(fileList)

                            makeSystHists(fileList)


    print('Finished')
