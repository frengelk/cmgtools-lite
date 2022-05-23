import ROOT
import time
import itertools
import PhysicsTools.Heppy.loadlibs
import array
import operator

from CMGTools.TTHAnalysis.treeReAnalyzer import *
from ROOT import TLorentzVector, TVector2, std

from math import sqrt, pi, acos, cos

#################
### Cuts and WP
#################

## Eta requirement
centralEta = 2.4
eleEta = 2.4

###########
# Jets
###########

corrJEC = "central" # can be "central","up","down"
JECAllowedValues = ["central","up","down"]
assert any(val==corrJEC for val in JECAllowedValues)

smearJER = "None"# can be "None","central","up","down"
JERAllowedValues = ["None","central","up","down"]
assert any(val==smearJER for val in JERAllowedValues)

print
print 30*'#'
print 'Going to use', corrJEC , 'JEC and', smearJER, 'JER!'
print 30*'#'

def getRecalcMET(metp4, event, corrJEC = "central", smearJER = "None"):
    ## newMETp4 = oldMETp4 - (Sum(oldJetsP4) - Sum(newJetsP4))

    # jet pT threshold for MET
    minJpt = 15

    # don't do anything for data
    if event.isData: return metp4

    # check jets for MET exist in tree, else use normal jets collection (Jet)
    jetName = "JetForMET"
    if not hasattr(event,"n"+jetName): jetName = "Jet"

    # get original jets used for MET:
    oldjets = [j for j in Collection(event,jetName,"n"+jetName)]
    # new jets will be old ones for now
    newjets = [j for j in Collection(event,jetName,"n"+jetName)]

    # filter jets
    oldjets = [j for j in oldjets if j.pt > minJpt]

    # vectorial summ of jets for MET
    deltaJetP4 = ROOT.TLorentzVector(0,0,0,0)
    for jet in oldjets: deltaJetP4 += jet.p4()

    if corrJEC == "central":
        #pass # don't do anything
        for jet in newjets: jet.pt = jet.rawPt * jet.corr
    elif corrJEC == "up":
        for jet in newjets: jet.pt = jet.rawPt * jet.corr_JECUp
    elif corrJEC == "down":
        for jet in newjets: jet.pt = jet.rawPt * jet.corr_JECDown
    if smearJER!= "None":
        for jet in newjets: jet.pt = returnJERSmearedPt(jet.pt,abs(jet.eta),jet.mcPt,smearJER)

    # filter jets
    newjets = [j for j in newjets if j.pt > minJpt]

    for jet in newjets: deltaJetP4 -= jet.p4()

    #print "MET diff = ", deltaJetP4.Pt()
    return (metp4 - deltaJetP4)

def returnJERSmearFactor(aeta, shiftJER):
    # from https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
    #13 TeV tables

    factor = 1.061 + shiftJER*0.023
    if   aeta > 3.2: factor = 1.320 + shiftJER * 0.286
    elif aeta > 3.0: factor = 1.303 + shiftJER * 0.111
    elif aeta > 2.5: factor = 1.343 + shiftJER * 0.123
    elif aeta > 1.9: factor = 1.126 + shiftJER * 0.094
    elif aeta > 1.3: factor = 1.106 + shiftJER * 0.030
    elif aeta > 0.8: factor = 1.088 + shiftJER * 0.029

    return factor

def returnJERSmearedPt(jetpt,aeta,genpt,smearJER):
    if genpt==0: return jetpt
#    assert (any(val==smearJER for val in JERAllowedValues) and smearJER!="None")
    shiftJER=0
    if   smearJER=="up"  : shiftJER = +1
    elif smearJER=="down": shiftJER = -1
    ptscale = max(0.0, (jetpt + (returnJERSmearFactor(aeta, shiftJER)-1)*(jetpt-genpt))/jetpt)
    return jetpt*ptscale

## B tag Working points
## CSV (v1 -- Run1) WPs
#btag_LooseWP = 0.244
#btag_TightWP = 0.679

## CMVA (PHYS14)
#btag_LooseWP = 0.244
#btag_TightWP = 0.762

## CSV v2 (CSV-IVF) ( PHYS14)
#btag_LooseWP = 0.423
#btag_MediumWP = 0.814
#btag_TightWP = 0.941

## CSV v2 (CSV-IVF) (Spring16)
#btag_LooseWP = 0.460
#btag_MediumWP = 0.800
#btag_TightWP = 0.935

# CSV v2 (CSV-IVF) (after remeasurement by BTV POG)
btag_LooseWP = 0.5426
btag_MediumWP = 0.8484
btag_TightWP = 0.9535

# DeepCSV (new Deep Flavour tagger)
btag_DeepLooseWP = 0.2219
btag_DeepMediumWP = 0.6324
btag_DeepTightWP = 0.8958

#DeepAK8 (brand new Deep Multiclass Tagger)
topTag_DeepAK8_LooseWP = 0.18
topTag_DeepAK8_MediumWP = 0.6
topTag_DeepAK8_TightWP = 0.89


###########
# MUONS
###########

muID = 'medium' # 'medium'(2015) or 'ICHEPmediumMuonId' (2016)



###########
# Electrons
###########

eleID = 'CB' # 'MVA' or 'CB'

print
print 30*'#'
print 'Going to use', eleID, 'electron ID!'
print 30*'#'
print

## PHYS14 IDs
## Non-triggering electron MVA id (Phys14 WP)
# Tight MVA WP
Ele_mvaPhys14_eta0p8_T = 0.73;
Ele_mvaPhys14_eta1p4_T = 0.57;
Ele_mvaPhys14_eta2p4_T = 0.05;
# Medium MVA WP  <--- UPDATE
Ele_mvaPhys14_eta0p8_M = 0.35;
Ele_mvaPhys14_eta1p4_M = 0.20;
Ele_mvaPhys14_eta2p4_M = -0.52;
# Loose MVA WP
Ele_mvaPhys14_eta0p8_L = 0.35;
Ele_mvaPhys14_eta1p4_L = 0.20;
Ele_mvaPhys14_eta2p4_L = -0.52;

## SPRING15 IDs
## Non-triggering electron MVA id (Spring15 WP):
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSLeptonSF#Electrons
# Tight MVA WP
Ele_mvaSpring15_eta0p8_T = 0.87;
Ele_mvaSpring15_eta1p4_T = 0.6;
Ele_mvaSpring15_eta2p4_T = 0.17;
# Medium MVA WP  <--- UPDATE
Ele_mvaSpring15_eta0p8_M = 0.35;
Ele_mvaSpring15_eta1p4_M = 0.20;
Ele_mvaSpring15_eta2p4_M = -0.52;
# Loose MVA WP
Ele_mvaSpring15_eta0p8_L = -0.16;
Ele_mvaSpring15_eta1p4_L = -0.65;
Ele_mvaSpring15_eta2p4_L = -0.74;
# VLoose MVA WP
Ele_mvaSpring15_eta0p8_VL = -0.11;
Ele_mvaSpring15_eta1p4_VL = -0.55;
Ele_mvaSpring15_eta2p4_VL = -0.74;

## Ele MVA check
def checkEleMVA(lep,WP = 'Tight', era = "Spring15" ):
    # Eta dependent MVA ID check:
    passID = False

    lepEta = abs(lep.eta)

    # eta cut
    if lepEta > eleEta:
        print "here"
        return False

    if era == "Spring15":
        lepMVA = lep.mvaIdSpring15

        if WP == 'Tight':
            if lepEta < 0.8: passID = lepMVA > Ele_mvaSpring15_eta0p8_T
            elif lepEta < 1.44: passID = lepMVA > Ele_mvaSpring15_eta1p4_T
            elif lepEta >= 1.57: passID = lepMVA > Ele_mvaSpring15_eta2p4_T
        elif WP == 'Medium':
            if lepEta < 0.8: passID = lepMVA > Ele_mvaSpring15_eta0p8_M
            elif lepEta < 1.44: passID = lepMVA > Ele_mvaSpring15_eta1p4_M
            elif lepEta >= 1.57: passID = lepMVA > Ele_mvaSpring15_eta2p4_M
        elif WP == 'Loose':
            if lepEta < 0.8: passID = lepMVA > Ele_mvaSpring15_eta0p8_L
            elif lepEta < 1.44: passID = lepMVA > Ele_mvaSpring15_eta1p4_L
            elif lepEta >= 1.57: passID = lepMVA > Ele_mvaSpring15_eta2p4_L
        elif WP == 'VLoose':
            if lepEta < 0.8: passID = lepMVA > Ele_mvaSpring15_eta0p8_VL
            elif lepEta < 1.44: passID = lepMVA > Ele_mvaSpring15_eta1p4_VL
            elif lepEta >= 1.57: passID = lepMVA > Ele_mvaSpring15_eta2p4_VL

    elif era == "Phys14":
        lepMVA = lep.mvaIdPhys14

        if WP == 'Tight':
            if lepEta < 0.8: passID = lepMVA > Ele_mvaPhys14_eta0p8_T
            elif lepEta < 1.44: passID = lepMVA > Ele_mvaPhys14_eta1p4_T
            elif lepEta >= 1.57: passID = lepMVA > Ele_mvaPhys14_eta2p4_T
        elif WP == 'Medium':
            if lepEta < 0.8: passID = lepMVA > Ele_mvaPhys14_eta0p8_M
            elif lepEta < 1.44: passID = lepMVA > Ele_mvaPhys14_eta1p4_M
            elif lepEta >= 1.57: passID = lepMVA > Ele_mvaPhys14_eta2p4_M
        elif WP == 'Loose':
            if lepEta < 0.8: passID = lepMVA > Ele_mvaPhys14_eta0p8_L
            elif lepEta < 1.44: passID = lepMVA > Ele_mvaPhys14_eta1p4_L
            elif lepEta >= 1.57: passID = lepMVA > Ele_mvaPhys14_eta2p4_L

    return passID

## Isolation
ele_miniIsoCut = 0.1
muo_miniIsoCut = 0.2
Lep_miniIsoCut = 0.4
trig_miniIsoCut = 0.8

## Lepton cuts (for MVAID)
goodEl_lostHits = 0
goodEl_sip3d = 4
goodMu_sip3d = 4

class EventVars1L_base:
    def __init__(self):

        self.branches = [
            ## general event info
            'Run','Lumi','Xsec',("Event","l"),'genWeight','isData',
            ## leptons
            'nLep', 'nVeto',
            'nEl','nMu',
            ## selected == tight leps
            #'nTightLeps',
            'nTightEl','nTightMu',
            # for indx
            ("nTightLeps","I"),("tightLepsIdx","I",10,"nTightLeps"),
            #("tightLeps_DescFlag","I",10,"nTightLeps"),
            'Lep_pdgId','Lep_pt','Lep_eta','Lep_phi','Lep_Idx','Lep_relIso','Lep_miniIso','Lep_hOverE',
            'Selected', # selected (tight) or anti-selected lepton
            # second leading lepton
            'Lep2_pt', 'Selected2',
            ## MET
            'MET','LT','ST',
            'MT',
            "DeltaPhiLepW", 'dPhi','Lp',
            "GendPhi","GenLT","GenMET",
            # no HF stuff
#            'METNoHF', 'LTNoHF', 'dPhiNoHF',
            ## jets
            'HT','nJets',('nBJet','I'), 'nBJetDeep',
            ("nJets30","I"),("Jets30Idx","I",50,"nJets30"),'nBJets30','nJets30Clean',
            'nJets40','nBJets40',
            "htJet30j", "htJet30ja","htJet40j",
            'Jet1_pt','Jet2_pt',
############################## FatJets, DeepAK8, additional BTag variables #########################################################
            #FatJets
            'nFatJets','FatJet1_pt','FatJet2_pt','FatJet1_eta','FatJet2_eta','FatJet1_phi','FatJet2_phi','FatJet1_mass','FatJet2_mass',("nDeepTop_loose","I"),("nDeepTop_medium","I"),("nDeepTop_tight","I"), ("nBJet_Excl_LooseTop_08","I"),("nBJet_Excl_MediumTop_08","I"),("nBJet_Excl_TightTop_08","I"), ("nBJetDeep_Excl_LooseTop_08","I"),("nBJetDeep_Excl_MediumTop_08","I"),("nBJetDeep_Excl_TightTop_08","I"),
            ('DeepAK8Top_Loose_pt_Array','F',15,'nDeepTop_loose'),
            ('DeepAK8Top_Loose_eta_Array','F',15,'nDeepTop_loose'),
            ('DeepAK8Top_Loose_phi_Array','F',15,'nDeepTop_loose'),
            ('Flag_Btag_leq_08_from_Loose_DeepAK8','I',15,'nBJet'),
            ('BTag_phi_Array','F',15,'nBJet'),
            ('BTag_eta_Array','F',15,'nBJet'),
            ('BTag_pt_Array','F',15,'nBJet'),
#################################################################################################
            ## top tags
            "nHighPtTopTag", "nHighPtTopTagPlusTau23",
            ## special Vars
            "LSLjetptGT80", # leading + subl. jet pt > 80
            'isSR', # is it Signal or Control region
            'Mll', #di-lepton mass
            'METfilters',
            #Datasets
            'PD_JetHT', 'PD_SingleEle', 'PD_SingleMu', 'PD_MET',
            'isDPhiSignal',
            'RA2_muJetFilter',
            'Flag_fastSimCorridorJetCleaning',
###################################################for PS Tune study ##############################################
            "nGenJets","nGenbJets","nGenJets30","nGenbJets30",
###################################################for Prefire study ##############################################
            "prefireW","prefireWup","prefireWdwn",
################################################### to get all the variables in the FR rather than trees ##############################################
            "met_caloPt","lheHTIncoming","genTau_grandmotherId","genTau_motherId","genLep_grandmotherId","genLep_motherId","DiLep_Flag","semiLep_Flag",
            ### new
            "pMSSM_id1", "pMSSM_id2",
            ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,keyvals):

        # prepare output
        #ret = dict([(name,-999.0) for name in self.branches])
        ret = {}
        for name in self.branches:
            if type(name) == 'tuple':
                ret[name] = []
            elif type(name) == 'str':
                ret[name] = -999

        ##############################
        ##############################
        # DATASET FLAG
        # -- needs to be adjusted manually
        ##############################
        ret['PD_JetHT'] = 0
        ret['PD_SingleEle'] = 0
        ret['PD_SingleMu'] = 0
        ret['PD_MET'] = 0
        ret['isDPhiSignal'] = 0

        if hasattr(event, 'prefireW'):
            ret['prefireW'] = event.prefireW
        if hasattr(event, 'prefireWup'):
            ret['prefireWup'] = event.prefireWup
        if hasattr(event, 'prefireWdwn'):
            ret['prefireWdwn'] = event.prefireWdwn


        if event.isData and hasattr(self,"sample"):
            if "JetHT" in self.sample: ret['PD_JetHT'] = 1
            elif "SingleEle" in self.sample: ret['PD_SingleEle'] = 1
            elif "SingleMu" in self.sample: ret['PD_SingleMu'] = 1
            elif "MET_" in self.sample: ret['PD_MET'] = 1
        if not event.isData and hasattr(self,"sample"):
            if "T1tttt" in self.sample or "T5qqqqWW" in self.sample:
                ret['isDPhiSignal'] = 1
        ##############################

        # copy basic event info:
        ret['Run'] = event.run
        ret['Event'] = event.evt
        ret['Lumi'] = event.lumi
        if hasattr(event, 'genWeight'):
            ret['genWeight'] = event.genWeight

        if hasattr(event,'xsec'):
            ret['Xsec'] = event.xsec

        if hasattr(event, 'isData'):
            ret['isData'] = event.isData


        genJets = []
        genbJets = []
        genJets30 = []
        genbJets30 = []
        # for checking the nGenBjets and nGenJets differences between 16/17 PS tunes and put every thing to FR rather than trees
        if not event.isData :
            genparts = [l for l in Collection(event,"GenPart","nGenPart")]
            for Gj in genparts:
                if (Gj.status !=23 or abs(Gj.pdgId) > 5): continue
                genJets.append(Gj)
                if Gj.pt > 30  : genJets30.append(Gj)
                if  Gj.pdgId == 5 : genbJets.append(Gj)
                if  Gj.pdgId == 5 and Gj.pt > 30 : genbJets30.append(Gj)
            if hasattr(event,'met_caloPt')           : ret["met_caloPt"]           = event.met_caloPt
            if hasattr(event,'lheHTIncoming')        : ret["lheHTIncoming"]        = event.lheHTIncoming
            genpTaus = [l for l in Collection(event,"genTau")]
            genpLeps = [l for l in Collection(event,"genLep")]
            for gtau in genpTaus :
                ret["genTau_grandmotherId"] = gtau.grandmotherId
                ret["genTau_motherId"]      = gtau.motherId
            for glep in genpLeps :
                ret["genLep_grandmotherId"] = glep.grandmotherId
                ret["genLep_motherId"]      = glep.motherId

            # add flag to distinguish between semilep/DiLep TTBar
            if "TTJets_DiLepton" in self.sample :
                if event.lheHTIncoming <= 600 :
                    ret["DiLep_Flag"] = 1
                else : ret["DiLep_Flag"] = 0

            if "TTJets_SingleLepton" in self.sample :
                if event.lheHTIncoming <= 600 :
                    ret["semiLep_Flag"] = 1
                else : ret["semiLep_Flag"] = 0

            if "TTJets_LO_HT" in self.sample :
                gtau_sum = sum([(abs(gt.grandmotherId)==6 and abs(gt.motherId)==24) for gt in genpTaus])
                glep_sum = sum([(abs(gl.grandmotherId)==6 and abs(gl.motherId)==24) for gl in genpLeps])
                if  ((gtau_sum + glep_sum) == 2) :
                    ret["DiLep_Flag"] = 1
                    ret["semiLep_Flag"] = 0
                elif  ((gtau_sum + glep_sum)) < 2 :
                    ret["semiLep_Flag"] = 1
                    ret["DiLep_Flag"] = 0
                else :
                    ret["DiLep_Flag"] = 0
                    ret["semiLep_Flag"] = 0

        ret["nGenJets"] = len(genJets)
        ret["nGenbJets"] = len(genbJets)
        ret["nGenJets30"] = len(genJets30)
        ret["nGenbJets30"] = len(genbJets30)

        leps = [l for l in Collection(event,"LepGood","nLepGood")]
        nlep = len(leps)

        ### LEPTONS
        Selected = False

        # selected good leptons
        selectedTightLeps = []
        selectedTightLepsIdx = []
        selectedVetoLeps = []

        # anti-selected leptons
        antiTightLeps = []
        antiTightLepsIdx = []
        antiVetoLeps = []

        for idx,lep in enumerate(leps):

            # for acceptance check
            lepEta = abs(lep.eta)

            # Pt cut
            if lep.pt < 10: continue

            # Iso cut -- to be compatible with the trigger
            if lep.miniRelIso > trig_miniIsoCut: continue

            ###################
            # MUONS
            ###################
            if(abs(lep.pdgId) == 13):
                if lepEta > 2.4: continue

                ## Lower ID is POG_LOOSE (see cfg)

                # ID, IP and Iso check:
                passID = 0
                if muID=='ICHEPmediumMuonId': passID = lep.ICHEPmediumMuonId
                else: passID = lep.mediumMuonId
                passIso = lep.miniRelIso < muo_miniIsoCut
                passIP = lep.sip3d < goodMu_sip3d

                # selected muons
                if passID and passIso and passIP:
                    selectedTightLeps.append(lep); selectedTightLepsIdx.append(idx)

                    antiVetoLeps.append(lep);
                else:
                    selectedVetoLeps.append(lep)

                # anti-selected muons
                if not passIso:
                    antiTightLeps.append(lep); antiTightLepsIdx.append(idx)
                else:
                    antiVetoLeps.append(lep);

            ###################
            # ELECTRONS
            ###################

            elif(abs(lep.pdgId) == 11):

                if lepEta > eleEta: continue

                # pass variables
                passIso = False
                passConv = False

                if eleID == 'CB':
                    # ELE CutBased ID
                    eidCB = lep.eleCBID_SPRING15_25ns_ConvVetoDxyDz

                    passTightID = (eidCB == 4)
                    passMediumID = (eidCB >= 3)
                    #passLooseID = (eidCB >= 2)
                    passVetoID = (eidCB >= 1)

                elif eleID == 'MVA':
                    # ELE MVA ID
                    # check MVA WPs
                    passTightID = checkEleMVA(lep,'Tight')
                    passLooseID = checkEleMVA(lep,'VLoose')

                # selected
                if passTightID:

                    # all tight leptons are veto for anti
                    antiVetoLeps.append(lep)

                    # Iso check:
                    if lep.miniRelIso < ele_miniIsoCut: passIso = True
                    # conversion check
                    if eleID == 'MVA':
                        if lep.lostHits <= goodEl_lostHits and lep.convVeto and lep.sip3d < goodEl_sip3d: passConv = True
                    elif eleID == 'CB':
                        passConv = True # cuts already included in POG_Cuts_ID_SPRING15_25ns_v1_ConvVetoDxyDz_X


                    passPostICHEPHLTHOverE = True # comment out again if (lep.hOverE < 0.04 and abs(lep.eta)>1.479) or abs(lep.eta)<=1.479 else False

                    # fill
                    if passIso and passConv and passPostICHEPHLTHOverE:
                        selectedTightLeps.append(lep); selectedTightLepsIdx.append(idx)
                    else:
                        selectedVetoLeps.append(lep)

                # anti-selected
                elif not passMediumID:#passVetoID:

                    # all anti leptons are veto for selected
                    selectedVetoLeps.append(lep)

                    # Iso check
                    passIso = lep.miniRelIso < Lep_miniIsoCut # should be true anyway
                    # other checks
                    passOther = False
                    if hasattr(lep,"hOverE"):
                        passOther = lep.hOverE > 0.01

                    # fill
                    if passIso and passOther:
                        antiTightLeps.append(lep); antiTightLepsIdx.append(idx)
                    else:
                        antiVetoLeps.append(lep)
                # Veto leptons
                elif passVetoID:
                    # the rest is veto for selected and anti
                    selectedVetoLeps.append(lep)
                    antiVetoLeps.append(lep)
        # end lepton loop

        ###################
        # EXTRA Loop for lepOther -- for anti-selected leptons
        ###################

        otherleps = [l for l in Collection(event,"LepOther","nLepOther")]
        #otherleps = []

        for idx,lep in enumerate(otherleps):

            # check acceptance
            lepEta = abs(lep.eta)
            if lepEta > 2.4: continue

            # Pt cut
            if lep.pt < 10: continue

            # Iso cut -- to be compatible with the trigger
            if lep.miniRelIso > trig_miniIsoCut: continue

            ############
            # Muons
            if(abs(lep.pdgId) == 13):
                ## Lower ID is POG_LOOSE (see cfg)

                # ID, IP and Iso check:
                #passID = lep.mediumMuonId == 1
                passIso = lep.miniRelIso > muo_miniIsoCut
                # cuts like for the LepGood muons
                #passIP = abs(lep.dxy) < 0.05 and abs(lep.dz) < 0.1

                #if passIso and passID and passIP:
                if passIso:
                    antiTightLeps.append(lep)
                    antiTightLepsIdx.append(idx)
                else:
                    antiVetoLeps.append(lep)

            ############
            # Electrons
            elif(abs(lep.pdgId) == 11):

                if(lepEta > eleEta): continue

                ## Iso selection: ele should have MiniIso < 0.4 (for trigger)
                if lep.miniRelIso > Lep_miniIsoCut: continue

                ## Set Ele IDs
                if eleID == 'CB':
                    # ELE CutBased ID
                    eidCB = lep.eleCBID_SPRING15_25ns_ConvVetoDxyDz

                    passMediumID = (eidCB >= 3)
                    passVetoID = (eidCB >= 1)
                else:
                    passMediumID = False
                    passVetoID = False

                # Cuts for Anti-selected electrons
                if not passMediumID:
                    # should always be true for LepOther

                    # other checks
                    passOther = False
                    if hasattr(lep,"hOverE"):
                        passOther = lep.hOverE > 0.01

                    #if not lep.conVeto:
                    if passOther:
                        antiTightLeps.append(lep)
                        antiTightLepsIdx.append(idx);
                    else:
                        antiVetoLeps.append(lep)

                elif passVetoID: #all Medium+ eles in LepOther
                    antiVetoLeps.append(lep)

        # choose common lepton collection: select selected or anti lepton
        if len(selectedTightLeps) > 0:
            tightLeps = selectedTightLeps
            tightLepsIdx = selectedTightLepsIdx

            vetoLeps = selectedVetoLeps

            ret['nTightLeps'] = len(tightLeps)
            ret['nTightMu'] = sum([ abs(lep.pdgId) == 13 for lep in tightLeps])
            ret['nTightEl'] = sum([ abs(lep.pdgId) == 11 for lep in tightLeps])

            ret['tightLepsIdx'] = tightLepsIdx

            ret['Selected'] = 1

            # Is second leading lepton selected, too?
            if len(selectedTightLeps) > 1:
                ret['Selected2'] = 1
            else:
                ret['Selected2'] = 0

        elif len(antiTightLeps) > 0:
            tightLeps = antiTightLeps
            tightLepsIdx = antiTightLepsIdx

            vetoLeps = antiVetoLeps

            ret['nTightLeps'] = 0
            ret['nTightMu'] = 0
            ret['nTightEl'] = 0

            ret['tightLepsIdx'] = []

            ret['Selected'] = -1

        else:
            tightLeps = []
            tightLepsIdx = []

            vetoLeps = []

            ret['nTightLeps'] = 0
            ret['nTightMu'] = 0
            ret['nTightEl'] = 0

            ret['tightLepsIdx'] = []

            ret['Selected'] = 0

        # store Tight and Veto lepton numbers
        ret['nLep'] = len(tightLeps)
        ret['nVeto'] = len(vetoLeps)

        # get number of tight el and mu
        tightEl = [lep for lep in tightLeps if abs(lep.pdgId) == 11]
        tightMu = [lep for lep in tightLeps if abs(lep.pdgId) == 13]

        ret['nEl'] = len(tightEl)
        ret['nMu'] = len(tightMu)

        # save leading lepton vars
        if len(tightLeps) > 0:
            ret['Lep_Idx'] = tightLepsIdx[0]

            ret['Lep_pt'] = tightLeps[0].pt
            ret['Lep_eta'] = tightLeps[0].eta
            ret['Lep_phi'] = tightLeps[0].phi
            ret['Lep_pdgId'] = tightLeps[0].pdgId

            ret['Lep_relIso'] = tightLeps[0].relIso03
            ret['Lep_miniIso'] = tightLeps[0].miniRelIso
            if hasattr(tightLeps[0],"hOverE"):
                ret['Lep_hOverE'] = tightLeps[0].hOverE

        elif len(leps) > 0: # fill it with leading lepton
            ret['Lep_Idx'] = 0

            ret['Lep_pt'] = leps[0].pt
            ret['Lep_eta'] = leps[0].eta
            ret['Lep_phi'] = leps[0].phi
            ret['Lep_pdgId'] = leps[0].pdgId

            ret['Lep_relIso'] = leps[0].relIso03
            ret['Lep_miniIso'] = leps[0].miniRelIso
            if hasattr(leps[0],"hOverE"):
                ret['Lep_hOverE'] = leps[0].hOverE
        else :
            ret['Lep_pt'] = -999
            ret['Lep_relIso'] = -999
            ret['Lep_miniIso'] = -999
        # save second leading lepton vars
        if len(tightLeps) > 1:
            ret['Lep2_pt'] = tightLeps[1].pt

        ########
        ### Jets
        ########
        jets = [j for j in Collection(event,"Jet","nJet")]
        njet = len(jets)

        # Apply JEC up/down variations if needed (only MC!)
        if event.isData == False:
            if corrJEC == "central":
                pass # don't do anything
                #for jet in jets: jet.pt = jet.rawPt * jet.corr
            elif corrJEC == "up":
                for jet in jets: jet.pt = jet.rawPt * jet.corr_JECUp
            elif corrJEC == "down":
                for jet in jets: jet.pt = jet.rawPt * jet.corr_JECDown
            else:
                pass
            if smearJER!= "None":
                for jet in jets: jet.pt = returnJERSmearedPt(jet.pt,abs(jet.eta),jet.mcPt,smearJER)

        centralJet30 = []; centralJet30idx = []
        centralJet40 = []

        ret['Flag_fastSimCorridorJetCleaning'] = 1
        for i,j in enumerate(jets):
            # Cleaning up of fastsim jets (from "corridor" studies) https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSRecommendationsMoriond17#Cleaning_up_of_fastsim_jets_from
            if ret['isDPhiSignal']: #only check for signals (see condition check above)
                if j.pt>20 and abs(j.eta)<2.5 and j.mcPt == 0 and j.chHEF<0.1: ret['Flag_fastSimCorridorJetCleaning'] = 0
            if j.pt>30 and abs(j.eta)<centralEta:
                centralJet30.append(j)
                centralJet30idx.append(i)
            if j.pt>40 and abs(j.eta)<centralEta:
                centralJet40.append(j)

        # jets 30 (cmg cleaning only)
        nJetC = len(centralJet30)
        ret['nJets']   = nJetC
        ret['nJets30']   = nJetC
        # store indeces
        ret['Jets30Idx'] = centralJet30idx
        #print "nJets30:", len(centralJet30), " nIdx:", len(centralJet30idx)

        # jets 40
        nJet40C = len(centralJet40)
        ret['nJets40']   = nJet40C

########################### FatJet #########################################################
        _DeepAK8Top_Loose_pt_Array  = []
        _DeepAK8Top_Loose_eta_Array = []
        _DeepAK8Top_Loose_phi_Array = []

        FatJets =[l for l in Collection(event,"FatJet","nFatJet")]
        nfatjet=len(FatJets)
        fatJets=[]

        nFatJetLoose = 0
        nFatJetMedium = 0
        nFatJetTight = 0

        for i,j in enumerate(FatJets):
              fatJets.append(j)

              if(j.raw_score_deep_Top_PUPPI > topTag_DeepAK8_LooseWP and j.pt>=400.):
                    nFatJetLoose+=1
                    _DeepAK8Top_Loose_pt_Array.append(j.pt)
                    _DeepAK8Top_Loose_eta_Array.append(j.eta)
                    _DeepAK8Top_Loose_phi_Array.append(j.phi)

              if(j.raw_score_deep_Top_PUPPI > topTag_DeepAK8_MediumWP and j.pt>=400.):
                   nFatJetMedium+=1

              if(j.raw_score_deep_Top_PUPPI > topTag_DeepAK8_TightWP and j.pt>=400.):
                   nFatJetTight+=1

        ret['nDeepTop_loose'] = nFatJetLoose
        ret['nDeepTop_medium'] = nFatJetMedium
        ret['nDeepTop_tight'] = nFatJetTight
        ret['DeepAK8Top_Loose_pt_Array'] = _DeepAK8Top_Loose_pt_Array
        ret['DeepAK8Top_Loose_eta_Array'] = _DeepAK8Top_Loose_eta_Array
        ret['DeepAK8Top_Loose_phi_Array'] = _DeepAK8Top_Loose_phi_Array


        if nfatjet>=1:
              ret['FatJet1_pt'] = fatJets[0].pt
              ret['FatJet1_eta'] = fatJets[0].eta
              ret['FatJet1_phi'] = fatJets[0].phi
              ret['FatJet1_mass'] = fatJets[0].mass



        if nfatjet>=2:
              ret['FatJet2_pt'] = fatJets[1].pt
              ret['FatJet2_eta'] = fatJets[1].eta
              ret['FatJet2_phi'] = fatJets[1].phi
              ret['FatJet2_mass'] = fatJets[1].mass


#####################################################################################################

        ##############################
        ## Local cleaning from leptons
        ##############################
        cJet30Clean = []
        dRminCut = 0.4

        # Do cleaning a la CMG: clean max 1 jet for each lepton (the nearest)
        cJet30Clean = centralJet30

        for lep in tightLeps:
            # don't clean LepGood, only LepOther
            if lep not in otherleps: continue

            jNear, dRmin = None, 99
            # find nearest jet
            for jet in centralJet30:

                dR = jet.p4().DeltaR(lep.p4())
                if dR < dRmin:
                    jNear, dRmin = jet, dR

            # remove nearest jet
            if dRmin < dRminCut:
                cJet30Clean.remove(jNear)

        if nJetC !=  len(cJet30Clean) and False:
            print "Non-clean jets: ", nJetC, "\tclean jets:", len(cJet30Clean)
            print jets
            print leps
            print otherleps

        # cleaned jets
        nJet30C = len(cJet30Clean)
        ret['nJets30Clean'] = len(cJet30Clean)

        if nJet30C > 0:
            ret['Jet1_pt'] = cJet30Clean[0].pt
        else: ret['Jet1_pt']  = -999
        if nJet30C > 1:
            ret['Jet2_pt'] = cJet30Clean[1].pt
        else: ret['Jet2_pt']  = -999
        # imho, use Jet2_pt > 80 instead
        ret['LSLjetptGT80'] = 1 if sum([j.pt>80 for j in cJet30Clean])>=2 else 0

        ret['htJet30j']  = sum([j.pt for j in cJet30Clean])
        ret['htJet30ja'] = sum([j.pt for j in jets if j.pt>30])

        ret['htJet40j']  = sum([j.pt for j in centralJet40])

        ret['HT'] = ret['htJet30j']

        ## B tagging WPs for CSVv2 (CSV-IVF)
        ## from: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideBTagging#Preliminary_working_or_operating

        # WP defined on top
        btagWP = btag_MediumWP

        BJetMedium30 = []
        BJetMedium40 = []

        nBJetDeep = 0

        _nBTag_out_Loose=0
        _nBTag_out_Medium=0
        _nBTag_out_Tight=0

        _nBTagDeep_out_Loose=0
        _nBTagDeep_out_Medium=0
        _nBTagDeep_out_Tight=0

        flag_leq_08_Loose_array = []
        BJet_pt_Array = []
        BJet_phi_Array = []
        BJet_eta_Array = []

        for i,j in enumerate(cJet30Clean):
            if j.btagCSV > btagWP:
                BJetMedium30.append(j)
###########################################################################
                BJet_pt_Array.append(j.pt)
                BJet_phi_Array.append(j.phi)
                BJet_eta_Array.append(j.eta)

                _BTag_phi=j.phi
                _BTag_eta=j.eta

                flag_leq_08_Loose=0
                flag_leq_08_Medium=0
                flag_leq_08_Tight=0

                for k,l in enumerate(FatJets):
                       if(l.raw_score_deep_Top_PUPPI>topTag_DeepAK8_LooseWP and l.pt>=400.):
                             _TopTag_Phi_Loose=l.phi
                             _TopTag_Eta_Loose=l.eta

                             _delta_phi_Loose=fabs(acos(cos(_TopTag_Phi_Loose-_BTag_phi)))
                             _delta_eta_Loose=fabs(_TopTag_Eta_Loose-_BTag_eta)
                             _delta_R_Loose=sqrt(pow(_delta_eta_Loose,2)+pow(_delta_phi_Loose,2))

                             if(_delta_R_Loose<0.8):
                                    flag_leq_08_Loose+=1

                       if(l.raw_score_deep_Top_PUPPI>topTag_DeepAK8_MediumWP and l.pt>=400.):
                             _TopTag_Phi_Medium=l.phi
                             _TopTag_Eta_Medium=l.eta

                             _delta_phi_Medium=fabs(acos(cos(_TopTag_Phi_Medium-_BTag_phi)))
                             _delta_eta_Medium=fabs(_TopTag_Eta_Medium-_BTag_eta)
                             _delta_R_Medium=sqrt(pow(_delta_eta_Medium,2)+pow(_delta_phi_Medium,2))

                             if(_delta_R_Medium<0.8):
                                    flag_leq_08_Medium+=1

                       if(l.raw_score_deep_Top_PUPPI>topTag_DeepAK8_TightWP and l.pt>=400.):
                             _TopTag_Phi_Tight=l.phi
                             _TopTag_Eta_Tight=l.eta

                             _delta_phi_Tight=fabs(acos(cos(_TopTag_Phi_Tight-_BTag_phi)))
                             _delta_eta_Tight=fabs(_TopTag_Eta_Tight-_BTag_eta)
                             _delta_R_Tight=sqrt(pow(_delta_eta_Tight,2)+pow(_delta_phi_Tight,2))

                             if(_delta_R_Tight<0.8):
                                    flag_leq_08_Tight+=1


                #print flag_leq_08_Loose
                flag_leq_08_Loose_array.append(flag_leq_08_Loose)
                if(flag_leq_08_Loose==0):
                       _nBTag_out_Loose+=1

                if(flag_leq_08_Medium==0):
                       _nBTag_out_Medium+=1

                if(flag_leq_08_Tight==0):
                       _nBTag_out_Tight+=1

            if (j.DFprobb + j.DFprobbb + j.DFproblepb) > 0.66:
                 nBJetDeep += 1

                 _BTagDeep_phi=j.phi
                 _BTagDeep_eta=j.eta

                 flagDeep_leq_08_Loose=0
                 flagDeep_leq_08_Medium=0
                 flagDeep_leq_08_Tight=0

                 for k,l in enumerate(FatJets):
                       if(l.raw_score_deep_Top_PUPPI>topTag_DeepAK8_LooseWP and l.pt>=400.):
                             _TopTag_Phi_Loose=l.phi
                             _TopTag_Eta_Loose=l.eta

                             _delta_phi_Loose=fabs(acos(cos(_TopTag_Phi_Loose-_BTagDeep_phi)))
                             _delta_eta_Loose=fabs(_TopTag_Eta_Loose-_BTagDeep_eta)
                             _delta_R_Loose=sqrt(pow(_delta_eta_Loose,2)+pow(_delta_phi_Loose,2))

                             if(_delta_R_Loose<0.8):
                                    flagDeep_leq_08_Loose+=1

                       if(l.raw_score_deep_Top_PUPPI>topTag_DeepAK8_MediumWP and l.pt>=400.):
                             _TopTag_Phi_Medium=l.phi
                             _TopTag_Eta_Medium=l.eta

                             _delta_phi_Medium=fabs(acos(cos(_TopTag_Phi_Medium-_BTagDeep_phi)))
                             _delta_eta_Medium=fabs(_TopTag_Eta_Medium-_BTagDeep_eta)
                             _delta_R_Medium=sqrt(pow(_delta_eta_Medium,2)+pow(_delta_phi_Medium,2))

                             if(_delta_R_Medium<0.8):
                                    flagDeep_leq_08_Medium+=1

                       if(l.raw_score_deep_Top_PUPPI>topTag_DeepAK8_TightWP and l.pt>=400.):
                             _TopTag_Phi_Tight=l.phi
                             _TopTag_Eta_Tight=l.eta

                             _delta_phi_Tight=fabs(acos(cos(_TopTag_Phi_Tight-_BTagDeep_phi)))
                             _delta_eta_Tight=fabs(_TopTag_Eta_Tight-_BTagDeep_eta)
                             _delta_R_Tight=sqrt(pow(_delta_eta_Tight,2)+pow(_delta_phi_Tight,2))

                             if(_delta_R_Tight<0.8):
                                    flagDeep_leq_08_Tight+=1



                 if(flagDeep_leq_08_Loose==0):
                       _nBTagDeep_out_Loose+=1

                 if(flagDeep_leq_08_Medium==0):
                       _nBTagDeep_out_Medium+=1

                 if(flagDeep_leq_08_Tight==0):
                       _nBTagDeep_out_Tight+=1


        ret['nBJetDeep'] = nBJetDeep

        ret['nBJet_Excl_LooseTop_08'] = _nBTag_out_Loose
        ret['nBJet_Excl_MediumTop_08'] = _nBTag_out_Medium
        ret['nBJet_Excl_TightTop_08'] = _nBTag_out_Tight

        ret['nBJetDeep_Excl_LooseTop_08'] = _nBTagDeep_out_Loose
        ret['nBJetDeep_Excl_MediumTop_08'] = _nBTagDeep_out_Medium
        ret['nBJetDeep_Excl_TightTop_08'] = _nBTagDeep_out_Tight

        ret['Flag_Btag_leq_08_from_Loose_DeepAK8'] = flag_leq_08_Loose_array

        ret['BTag_pt_Array'] = BJet_pt_Array
        ret['BTag_phi_Array'] = BJet_phi_Array
        ret['BTag_eta_Array'] = BJet_eta_Array
#####################################################################################

       # if (j.DFprobb + j.DFprobbb) >  0.0574 :
       #         nBJetDeep += 1

        for i,j in enumerate(centralJet40):
            if j.btagCSV > btagWP:
                BJetMedium40.append(j)

        # using cleaned collection!
        ret['nBJet']   = len(BJetMedium30)
        ret['nBJets30']   = len(BJetMedium30)

      #  ret['nBJetDeep'] = nBJetDeep

        # using normal collection
        ret['nBJets40']   = len(BJetMedium40)

        ######
        # MET
        #####
        metp4 = ROOT.TLorentzVector(0,0,0,0)
        if hasattr(event, 'metMuEGClean_pt'):
            metp4.SetPtEtaPhiM(event.metMuEGClean_pt,event.metMuEGClean_eta,event.metMuEGClean_phi,event.metMuEGClean_mass)
        else:
            metp4.SetPtEtaPhiM(event.met_pt,event.met_eta,event.met_phi,event.met_mass)

        # recalc MET
        if corrJEC != "central" or smearJER!= "None":
            ## get original jet collection
            metp4 = getRecalcMET(metp4,event,corrJEC,smearJER)

        Genmetp4 = ROOT.TLorentzVector(0,0,0,0)

        if not event.isData:
            Genmetp4.SetPtEtaPhiM(event.met_genPt,event.met_genEta,event.met_genPhi,0)

        ret["MET"] = metp4.Pt()

        ## MET NO HF
#        metNoHFp4 = ROOT.TLorentzVector(0,0,0,0)
#        metNoHFp4.SetPtEtaPhiM(event.metNoHF_pt,event.metNoHF_eta,event.metNoHF_phi,event.metNoHF_mass)
#        ret["METNoHF"] = metNoHFp4.Pt()

        ## MET FILTERS for data
        if event.isData:
            ret['METfilters'] = event.Flag_goodVertices and event.Flag_HBHENoiseFilter and event.Flag_eeBadScFilter and event.Flag_HBHENoiseIsoFilter and event.Flag_EcalDeadCellTriggerPrimitiveFilter and event.Flag_BadPFMuonFilter and event.Flag_globalTightHalo2016Filter
        else:
            ret['METfilters'] = 1


        # deltaPhi between the (single) lepton and the reconstructed W (lep + MET)
        dPhiLepW = -999 # set default value to -999 to spot "empty" entries
        GendPhiLepW = -999 # set default value to -999 to spot "empty" entries
#        dPhiLepWNoHF = -999 # set default value to -999 to spot "empty" entries
        # LT of lepton and MET
        LT = -999
        GenLT = -999
#        LTNoHF = -999
        Lp = -99
        MT = -99

        if len(tightLeps) >=1:
            recoWp4 =  tightLeps[0].p4() + metp4
            GenrecoWp4 =  tightLeps[0].p4() + Genmetp4
            GendPhiLepW = tightLeps[0].p4().DeltaPhi(GenrecoWp4)
            GenLT = tightLeps[0].pt + Genmetp4.Pt()
            dPhiLepW = tightLeps[0].p4().DeltaPhi(recoWp4)
            LT = tightLeps[0].pt + metp4.Pt()
            Lp = tightLeps[0].pt / recoWp4.Pt() * cos(dPhiLepW)

            #MT = recoWp4.Mt() # doesn't work
            MT = sqrt(2*metp4.Pt()*tightLeps[0].pt * (1-cos(dPhiLepW)))

            ## no HF
#            recoWNoHFp4 =  tightLeps[0].p4() + metNoHFp4
#            dPhiLepWNoHF = tightLeps[0].p4().DeltaPhi(recoWNoHFp4)
#            LTNoHF = tightLeps[0].pt + event.metNoHF_pt

        ret["DeltaPhiLepW"] = dPhiLepW
        dPhi = abs(dPhiLepW) # nickname for absolute dPhiLepW
        ret['dPhi'] = dPhi
        ret['ST'] = LT
        ret['LT'] = LT
        ret['Lp'] = Lp
        ret['MT'] = MT
        ret['GendPhi'] = abs(GendPhiLepW)
        ret['GenLT'] = GenLT
        ret['GenMET'] = Genmetp4.Pt()
        # no HF
#        dPhiNoHF = abs(dPhiLepWNoHF) # nickname for absolute dPhiLepW
#        ret['dPhiNoHF'] = dPhiNoHF
#        ret['LTNoHF'] = LTNoHF

        #####################
        ## SIGNAL REGION FLAG
        #####################
        ret["pMSSM_id1"] = event.pMSSM_id1
        ret["pMSSM_id2"] = event.pMSSM_id2
        #from IPython import embed;embed()
        ## Signal region flag
        # isSR SR vs CR flag
        isSR = 0

        # 0-B SRs -- simplified dPhi
        if ret['nBJet'] == 0:
            if LT < 250:   isSR = 0
            elif LT > 250: isSR = dPhi > 0.75
            # BLIND data
            if event.isData and nJet30C >= 5:
                isSR = - isSR
        # Multi-B SRs
        elif nJet30C < 99:
            if LT < 250:   isSR = 0
            elif LT < 350: isSR = dPhi > 1.0
            elif LT < 600: isSR = dPhi > 0.75
            elif LT > 600: isSR = dPhi > 0.5

            # BLIND data
            if event.isData and nJet30C >= 6:
                isSR = - isSR

        ret['isSR'] = isSR

        #############
        ## Playground
        #############

        # di-lepton mass: opposite-sign, same flavour
        Mll = 0

        if len(tightLeps) > 1:

            lep1 = tightLeps[0]
            id1 = lep1.pdgId

            for lep2 in leps[1:]:
                if lep2.pdgId + lep1.pdgId == 0:
                    dilepP4 = lep1.p4() + lep2.p4()
                    Mll = dilepP4.M()

        ret['Mll'] = Mll

        # RA2 proposed filter
        ret['RA2_muJetFilter'] = True
        for j in cJet30Clean:
            if j.pt > 200 and j.muEF > 0.5 and abs(acos(cos(j.phi-metp4.Phi()))) > (pi - 0.4):
                ret['RA2_muJetFilter'] = False

        return ret

# Main function for test
if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf = EventVars1L_base()
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
            print self.sf(ev,{})
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)
