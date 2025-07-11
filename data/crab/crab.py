from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config

config = config()

config.section_("General")
config.General.transferOutputs = True
config.General.transferLogs = True
config.General.requestName = '@@JobBatchName@@'
config.General.workArea = 'crab_projects'

config.section_("JobType")
config.JobType.pluginName = 'PrivateMC'
config.JobType.allowUndistributedCMSSW = True
config.JobType.numCores = 4
config.JobType.maxMemoryMB = @@RequestMemory@@
config.JobType.maxJobRuntimeMin = @@minutes@@


config.JobType.scriptExe = "@@SUBMITDIR@@/run.sh"
# hadd nano will not be needed once nano tools are in cmssw
config.JobType.inputFiles = [@@transfer_input_files@@]
config.JobType.psetName = "PSet.py"
config.JobType.outputFiles = [@@output_files@@]

config.section_("Data")

config.Data.splitting = 'EventBased'
config.Data.outputPrimaryDataset = '@@JobBatchName@@'
config.Data.unitsPerJob = @@nevents@@
NJOBS = @@njobs@@  # This is not a configuration parameter, but an auxiliary variable that we use in the next line.
config.Data.totalUnits = config.Data.unitsPerJob * NJOBS
config.Data.publication = False
config.Data.outputDatasetTag = 'SampleFactory'
config.Data.outLFNDirBase = '@@OUTDIR@@'

config.section_("Site")
config.Site.storageSite = '@@SITE@@'
