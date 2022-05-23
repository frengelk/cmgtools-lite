import os
from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.transferLogs = True

# user variables
config.section_("User")
#config.User.voRole = "dcms"
#config.User.voGroup = "dcms"

config.section_("JobType")
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'heppy_crab_fake_pset.py'
config.JobType.scriptExe = 'heppy_crab_script.sh'
config.JobType.disableAutomaticOutputCollection = True
# config.JobType.sendPythonFolder = True  #doesn't work, not supported yet? do it by hand

# 'python.tar.gz', 'FatJetNN_104X_MC.py',
config.JobType.inputFiles = ['FrameworkJobReport.xml', 'heppy_crab_script.py', 'cmgdataset.tar.gz', 'python.tar.gz', 'cafpython.tar.gz', 'options.json', 'FatJetNN_94X_data.py', 'FatJetNN_94X_MC.py', 'FatJetNN_104X_MC.py', 'FatJetNN_104X_data.py']
config.JobType.outputFiles = []
# request more RAM
config.JobType.maxMemoryMB = 3500 # 4000

config.section_("Data")
config.Data.inputDBS = 'global'
config.Data.splitting = 'EventBased'
config.Data.outLFNDirBase = '/store/user/' + os.environ["USER"]
config.Data.publication = False
#config.Data.totalUnits = 10000
config.Data.unitsPerJob = 1000
#config.Data.totalUnits = 200

config.section_("Site")

# print("\nconfig\n")
#from IPython import embed; embed()
