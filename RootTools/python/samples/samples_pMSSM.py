import PhysicsTools.HeppyCore.framework.config as cfg
import os

#####COMPONENT CREATOR

from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator

kreator = ComponentCreator()

### pMSSM
# SMS_T5qqqqVV_TuneCUETP8M1 = kreator.makeMCComponent("SMS_T5qqqqVV_TuneCUETP8M1","/SMS-T5qqqqVV_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUSummer16v3Fast_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM","CMS",".*root")
# SMS_T5qqqqVV_TuneCP2 = kreator.makeMCComponent("SMS_T5qqqqVV_TuneCP2","/SMS-T5qqqqVV_TuneCP2_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_94X_mc2017_realistic_v15-v1/MINIAODSIM","CMS",".*root")
# SMS_T5qqqqVV_TuneCP2_ext = kreator.makeMCComponent("SMS_T5qqqqVV_TuneCP2_ext","/SMS-T5qqqqVV_TuneCP2_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_94X_mc2017_realistic_v15_ext1-v1/MINIAODSIM","CMS",".*root")


# mcSamplesT5qqqqVV = [SMS_T5qqqqVV_TuneCUETP8M1,SMS_T5qqqqVV_TuneCP2,SMS_T5qqqqVV_TuneCP2_ext]
# SMS_T1ttttCP5_MVA = kreator.makeMCComponentFromLocal("SMS_T1ttttCP5_MVA","LOCAL","/pnfs/desy.de/cms/tier2/store/user/amohamed/SMS-T1tttt_mglu1900_mlsp100_full-sim_MiniAOD/T1tttt_mglu1900_mlsp100_full-sim_PREMIX/SMS-T1tttt_mglu1900_mlsp100_full-sim_MiniAOD/210311_111328/0000",".*root")

PMSSM_set_2_prompt_2_TuneCP2 = kreator.makeMCComponent(
    "PMSSM_set_2_prompt_2_TuneCP2",
    "/PMSSM_set_2_prompt_2_TuneCP2_13TeV-pythia8/RunIIAutumn18MiniAOD-PUFall18Fast_GridpackScan_102X_upgrade2018_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)


PMSSM_set_2_prompt_1_TuneCP2_v15_v2 = kreator.makeMCComponent(
    "PMSSM_set_2_prompt_1_TuneCP2_v15_v2",
    "/PMSSM_set_2_prompt_1_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_2_prompt_1_TuneCP2_v15_v4 = kreator.makeMCComponent(
    "PMSSM_set_2_prompt_1_TuneCP2_v15_v4",
    "/PMSSM_set_2_prompt_1_TuneCP2_13TeV-pythia8/RunIIAutumn18MiniAOD-PUFall18Fast_GridpackScan_102X_upgrade2018_realistic_v15-v4/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_prompt_3_TuneCP2_v15_v2 = kreator.makeMCComponent(
    "PMSSM_set_1_prompt_3_TuneCP2_v15_v2",
    "/PMSSM_set_1_prompt_3_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_prompt_3_TuneCP2_v15_v2 = kreator.makeMCComponent(
    "PMSSM_set_1_prompt_3_TuneCP2_v15_v2",
    "/PMSSM_set_1_prompt_3_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_prompt_2_TuneCP2_PU18_v15_v1 = kreator.makeMCComponent(
    "PMSSM_set_1_prompt_2_TuneCP2_PU18_v15_v1",
    "/PMSSM_set_1_prompt_2_TuneCP2_13TeV-pythia8/RunIIAutumn18MiniAOD-PUFall18Fast_GridpackScan_102X_upgrade2018_realistic_v15-v1/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_prompt_2_TuneCP2_PU17_v15_v1 = kreator.makeMCComponent(
    "PMSSM_set_1_prompt_2_TuneCP2_PU17_v15_v1",
    "/PMSSM_set_1_prompt_2_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v1/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_prompt_1_TuneCP2_Autumn18_PU18_v15_v1 = kreator.makeMCComponent(
    "PMSSM_set_1_prompt_1_TuneCP2_Autumn18_PU18_v15_v1",
    "/PMSSM_set_1_prompt_1_TuneCP2_13TeV-pythia8/RunIIAutumn18MiniAOD-PUFall18Fast_GridpackScan_102X_upgrade2018_realistic_v15-v1/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_prompt_1_TuneCP2_PU17_v15_v2 = kreator.makeMCComponent(
    "PMSSM_set_1_prompt_1_TuneCP2_PU17_v15_v2",
    "/PMSSM_set_1_prompt_1_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_2_LL_2_TuneCP2_PU17_v15_v2 = kreator.makeMCComponent(
    "PMSSM_set_2_LL_2_TuneCP2_PU17_v15_v2",
    "/PMSSM_set_2_LL_2_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_2_LL_1_TuneCP2_PU18_v15_v3 = kreator.makeMCComponent(
    "PMSSM_set_2_LL_1_TuneCP2_PU18_v15_v3",
    "/PMSSM_set_2_LL_1_TuneCP2_13TeV-pythia8/RunIIAutumn18MiniAOD-PUFall18Fast_GridpackScan_102X_upgrade2018_realistic_v15-v3/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_2_LL_1_TuneCP2_PU17_v15_v2 = kreator.makeMCComponent(
    "PMSSM_set_2_LL_1_TuneCP2_PU17_v15_v2",
    "/PMSSM_set_2_LL_1_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_LL_TuneCP2_PU18_v15_v1 = kreator.makeMCComponent(
    "PMSSM_set_1_LL_TuneCP2_PU18_v15_v1",
    "/PMSSM_set_1_LL_TuneCP2_13TeV-pythia8/RunIIAutumn18MiniAOD-PUFall18Fast_GridpackScan_102X_upgrade2018_realistic_v15-v1/MINIAODSIM",
    "CMS",
    ".*root",
)

PMSSM_set_1_LL_TuneCP2_PU17_v15_v2 = kreator.makeMCComponent(
    "PMSSM_set_1_LL_TuneCP2_PU17_v15_v2",
    "/PMSSM_set_1_LL_TuneCP2_13TeV-pythia8/RunIIFall17MiniAODv2-PUFall17Fast_GridpackScan_94X_mc2017_realistic_v15-v2/MINIAODSIM",
    "CMS",
    ".*root",
)


# local file
pMSSM_local = kreator.makeMCComponentFromLocal(
    "pMSSM_local",
    "pMSSM",
    "/nfs/dust/cms/user/frengelk/examples/pMSSM/pMSSM_DAS",
)


mcSamples = [
PMSSM_set_1_LL_TuneCP2_PU17_v15_v2,
PMSSM_set_1_LL_TuneCP2_PU18_v15_v1,
PMSSM_set_1_prompt_1_TuneCP2_Autumn18_PU18_v15_v1,
PMSSM_set_1_prompt_1_TuneCP2_PU17_v15_v2,
PMSSM_set_1_prompt_2_TuneCP2_PU17_v15_v1,
PMSSM_set_1_prompt_2_TuneCP2_PU18_v15_v1,
PMSSM_set_1_prompt_3_TuneCP2_v15_v2,
PMSSM_set_2_prompt_1_TuneCP2_v15_v2,
PMSSM_set_2_prompt_1_TuneCP2_v15_v4
]
samples = mcSamples
dataSamples = []


### ---------------------------------------------------------------------

from CMGTools.TTHAnalysis.setup.Efficiencies import *

dataDir = "$CMSSW_BASE/src/CMGTools/TTHAnalysis/data"

# Define splitting
for comp in mcSamples:
    comp.isMC = True
    comp.isData = False
    comp.splitFactor = 250  #  if comp.name in [ "WJets", "DY3JetsM50", "DY4JetsM50","W1Jets","W2Jets","W3Jets","W4Jets","TTJetsHad" ] else 100
    comp.puFileMC = dataDir + "/puProfile_Summer12_53X.root"
    comp.puFileData = dataDir + "/puProfile_Data12.root"
    comp.efficiency = eff2012

for comp in dataSamples:
    comp.splitFactor = 1000
    comp.isMC = False
    comp.isData = True

if __name__ == "__main__":
    import sys

    if "test" in sys.argv:
        from CMGTools.RootTools.samples.ComponentCreator import testSamples

        testSamples(samples)
