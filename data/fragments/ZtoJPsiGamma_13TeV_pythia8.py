import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

generator = cms.EDFilter("Pythia8ConcurrentGeneratorFilter",
                         pythiaPylistVerbosity = cms.untracked.int32(1),
                         filterEfficiency = cms.untracked.double(1),
                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                         #crossSection = cms.untracked.double(1256000.0),
                         comEnergy = cms.double(13600.0),
                         maxEventsToPrint = cms.untracked.int32(0),
                         PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        processParameters = cms.vstring(
              'HiggsSM:ffbar2H =true',
              '25:m0 = 91.187600000001', #don't know why, but the Higgs mass can't be the same of Z0
              '25:mWidth = 2.49520',
              '25:mMin = 10.00000',
              '25:mMax = 0.00000',
              '25:spinType = 3', #(2S+1)
              '25:onMode = off',
              '25:addChannel = 1  1.00   103   22   443',
              '25:onIfMatch = 22 443',
              '443:onMode = off',    # ignore cross-section re-weighting (CSAMODE=6) since selecting wanted decay mode
              '443:onIfAny = 13',
            ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'processParameters',
                                    'pythia8PSweightsSettings',
                                    )
        )
)
ProductionFilterSequence = cms.Sequence(generator)
