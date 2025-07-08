import FWCore.ParameterSet.Config as cms


gridpackPath="root://eoscms.cern.ch//eos/cms/store/cmst3/group/l1tr/pviscone/Scouting/gridpacks/Xee/Mass5_slc7_amd64_gcc900_CMSSW_12_0_2_tarball.tar.xz"

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring(gridpackPath),
    nEvents = cms.untracked.uint32(200000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    generateConcurrently = cms.untracked.bool(True),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_xrootd.sh')
)

from Configuration.Generator.Pythia8CommonSettings_cfi import pythia8CommonSettingsBlock
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CP5Settings',
            #'processParameters'
        ),
        #processParameters = cms.vstring(),
    ),
    comEnergy = cms.double(14000.0),
    filterEfficiency = cms.untracked.double(1.0),
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    pythiaPylistVerbosity = cms.untracked.int32(1)
)

