from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from math import floor
import re

from DataFormats.FWLite import Lumis,Handle

class susyParameterScanAnalyzer( Analyzer ):
    """Get information for susy parameter scans    """
    def __init__(self, cfg_ana, cfg_comp, looperName ):
        super(susyParameterScanAnalyzer,self).__init__(cfg_ana,cfg_comp,looperName)
        self.susyParticles = {
            100001 : 'Squark',
            (1000000 + 21) : 'Gluino',
            (1000000 + 39) : 'Gravitino',
            (1000000 + 5) : 'Sbottom',
            (2000000 + 5) : 'Sbottom2',
            (1000000 + 6) : 'Stop',
            (2000000 + 6) : 'Stop2',
            (1000000 + 15) : 'Stau',
            (2000000 + 15) : 'Stau2',
            (1000000 + 16) : 'SnuTau',
            (1000000 + 22) : 'Neutralino',
            (1000000 + 23) : 'Neutralino2',
            (1000000 + 25) : 'Neutralino3',
            (1000000 + 35) : 'Neutralino4',
            (1000000 + 24) : 'Chargino',
            (1000000 + 37) : 'Chargino2',
        }
        self.LHEInfos=[]
        self.lumiCounter=-1
        self.currentLumi=0

    #---------------------------------------------
    # DECLARATION OF HANDLES OF GEN LEVEL OBJECTS
    #---------------------------------------------


    def declareHandles(self):
        print("\ndeclarehandles\n")
        super(susyParameterScanAnalyzer, self).declareHandles()
        if not self.cfg_comp.isMC: return True

        #mc information
        self.mchandles['genParticles'] = AutoHandle( 'prunedGenParticles',
                                                     'std::vector<reco::GenParticle>' )


        if self.cfg_ana.doLHE:
            if not self.cfg_ana.useLumiInfo:
                self.mchandles['lhe'] = AutoHandle( 'generator', 'GenLumiInfoHeader', mayFail = True, lazy = False )
            else:
                self.mchandles['GenInfo'] = AutoHandle( ('generator','',''), 'GenEventInfoProduct' )
                self.genLumiHandle = Handle("GenLumiInfoHeader")

        #from IPython import embed; embed()

        #GenLumiInfoHeader
    def beginLoop(self, setup):
        super(susyParameterScanAnalyzer,self).beginLoop(setup)

        print("\nbeginLoop\n")
        #print(self.cfg_comp.isMC)
        #print(self.cfg_ana.doLHE)
        #print(self.cfg_ana.useLumiInfo)

        #if not self.cfg_comp.isMC: return True
        if self.cfg_ana.doLHE and self.cfg_ana.useLumiInfo:
            lumis_first = Lumis(self.cfg_comp.files)
            lumis_second = Lumis(setup.config.components[0].options.secondaryInputFiles)
            print("\ncomp_files", self.cfg_comp.files)
            for lumi in lumis_second:
                #from IPython import embed;embed()
                if lumi.getByLabel('generator',self.genLumiHandle):
                    self.LHEInfos.append( self.genLumiHandle.product().configDescription() )
                else:
                    self.LHEInfos.append(lumi.aux().id().luminosityBlock())

        #lheprod=self.LHEInfos[self.lumiCounter]
        #pMSSM_id1 = int(lheprod.replace(".slha","").split("_")[-2])
        #pMSSM_id2 = int(lheprod.replace(".slha","").split("_")[-1])


    def findSusyMasses(self,event):
        #print("\nfindSusyMasses\n")
        #from IPython import embed;embed()
        masses = {}
        for p in event.genParticles:
            id = abs(p.pdgId())
            if (id / 1000000) % 10 in [1,2]:
                particle = None
                if id % 100 in [1,2,3,4]:
                    particle = "Squark"
                elif id in self.susyParticles:
                    particle = self.susyParticles[id]
                if particle != None:
                    if particle not in masses: masses[particle] = []
                    masses[particle].append(p.mass())
        for p,ms in masses.iteritems():
            avgmass = floor(sum(ms)/len(ms)+0.5)
            setattr(event, "genSusyM"+p, avgmass)

    def readLHE(self,event):
        #print " validity ", self.genLumiHandle.product().configDescription()
        print("\n readLHE\n")
        if not self.mchandles['lhe'].isValid():
            if not hasattr(self,"warned_already"):
                print "ERROR: Missing LHE header in file"
                self.warned_already = True
            return
        lheprod = self.mchandles['lhe'].configDescription();#product()

        scanline = re.compile(r"#\s*model\s+([A-Za-z0-9]+)_((\d+\.?\d*)(_\d+\.?\d*)*)(\s+(\d+\.?\d*))*\s*")
        for i in xrange(lheprod.comments_size()):
            comment = lheprod.getComment(i)
            if (not hasattr(self,'model_printed')) and ('model' in comment):
                print 'LHE contains this model string: %s (will not print the ones in the following events)'%comment
                self.model_printed = True
            m = re.match(scanline, comment)
            if m:
                event.susyModel = m.group(1)
                masses = [float(x) for x in m.group(2).split("_")]
                if len(masses) >= 1: event.genSusyMScan1 = masses[0]
                if len(masses) >= 2: event.genSusyMScan2 = masses[1]
                if len(masses) >= 3: event.genSusyMScan3 = masses[2]
                if len(masses) >= 4: event.genSusyMScan4 = masses[3]
            elif "model" in comment:
                if not hasattr(self,"warned_already"):
                    print "ERROR: I can't understand the model: ",comment
                    self.warned_already = True

    def readLHELumiInfo(self, event):
        if event.input.eventAuxiliary().id().luminosityBlock()!=self.currentLumi:
            self.currentLumi=event.input.eventAuxiliary().id().luminosityBlock()
            self.lumiCounter+=1

        lheprod=self.LHEInfos[self.lumiCounter]
        #print("\n--------readLHELumiInfo----------------")
        #print(lheprod)
        return lheprod

        #event.pMSSM_id1 = int(lheprod.replace(".slha","").split("_")[-2])
        #event.pMSSM_id2 = int(lheprod.replace(".slha","").split("_")[-1])
        """
        scanlineT1tttt = re.compile(r"([A-Za-z0-9]+)_((\d+\.?\d*)(_\d+\.?\d*)*)(\s+(\d+\.?\d*))*\s*")
        scanlineTChi = re.compile(r"([A-Za-z0-9]+)_([A-Za-z0-9]+)_((\d+\.?\d*)(_\d+\.?\d*)*)(\s+(\d+\.?\d*))*\s*")
        scanlineT2tt = re.compile(r"([A-Za-z0-9]+)_([A-Za-z0-9]+)-([A-Za-z0-9]+)_([A-Za-z0-9]+)_((\d+\.?\d*)(_\d+\.?\d*)*)(\s+(\d+\.?\d*))*\s*")

        mT1tttt = re.match(scanlineT1tttt, lheprod)
        mTChi   = re.match(scanlineTChi, lheprod)
        mT2tt   = re.match(scanlineT2tt, lheprod)

        #print lheprod, mT1tttt, mTChi, mT2tt

        if mT1tttt:
            event.susyModel = mT1tttt.group(1)
            masses = [float(x) for x in mT1tttt.group(2).split("_")]
            if len(masses) >= 1: event.genSusyMScan1 = masses[0]
            if len(masses) >= 2: event.genSusyMScan2 = masses[1]
            if len(masses) >= 3: event.genSusyMScan3 = masses[2]
            if len(masses) >= 4: event.genSusyMScan4 = masses[3]
        elif mTChi:
            event.susyModel = mTChi.group(1)
            masses = [float(x) for x in mTChi.group(3).split("_")]
            if len(masses) >= 1: event.genSusyMScan1 = masses[0]
            if len(masses) >= 2: event.genSusyMScan2 = masses[1]
            if len(masses) >= 3: event.genSusyMScan3 = masses[2]
            if len(masses) >= 4: event.genSusyMScan4 = masses[3]
        elif mT2tt:
            event.susyModel = mT2tt.group(1)
            masses = [float(x) for x in mT2tt.group(5).split("_")]
            if len(masses) >= 1: event.genSusyMScan1 = masses[0]
            if len(masses) >= 2: event.genSusyMScan2 = masses[1]
            if len(masses) >= 3: event.genSusyMScan3 = masses[2]
            if len(masses) >= 4: event.genSusyMScan4 = masses[3]

        """

    def process(self, event):
        #print("\nprocess lumi counter:", self.lumiCounter)
        lheprod=self.readLHELumiInfo(event)
        #print(lheprod)
        #rLI = self.readLHELumiInfo(event)
        #print("rLI")
        #print(rLI)
        # if not MC, nothing to do
        #lumis = Lumis(self.cfg_comp.files)
        #print(lumis.aux().id().luminosityBlock())
        event.pMSSM_id1 = int(lheprod.replace(".slha","").split("_")[-2])
        event.pMSSM_id2 = int(lheprod.replace(".slha","").split("_")[-1])
        #from IPython import embed;embed()
        #event.pMSSM_id1 = int(lheprod)
        #event.pMSSM_id2 = int(lheprod)
        if not self.cfg_comp.isMC:
            return True

        #print("event stats: id1, id2, lumicounter", event.pMSSM_id1, event.pMSSM_id2, self.lumiCounter)

        self.readCollections( event.input )

        # create parameters
        event.susyModel = None
        if not event.susyModel and self.susyParticles:
            event.susyModel = 'Unknown'
        for id,X in self.susyParticles.iteritems():
            setattr(event, "genSusyM"+X, -99.0)
        event.genSusyMScan1 = 0.0
        event.genSusyMScan2 = 0.0
        event.genSusyMScan3 = 0.0
        event.genSusyMScan4 = 0.0

        # do MC level analysis
        if self.cfg_ana.doLHE:
            if not self.cfg_ana.useLumiInfo:
                self.readLHE(event)
        #    else:
        #        self.readLHELumiInfo(event)
        self.findSusyMasses(event)
        return True
