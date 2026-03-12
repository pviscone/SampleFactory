import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *



generator = cms.EDFilter("Pythia8ConcurrentGeneratorFilter",
                         comEnergy = cms.double(14000.0),
                         maxEventsToPrint = cms.untracked.int32(1),
                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                         pythiaPylistVerbosity = cms.untracked.int32(1),
                         PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'WeakSingleBoson:ffbar2gmZ = on',
            '23:onMode = off',
            '23:onIfAny = 11',
            '23:mMin = 1.',
            '23:mMax = 10.',
            'PhaseSpace:mHatMin = 1.0', 
            'PhaseSpace:mHatMax = 10.0',
            'WeakZ0:gmZmode = 0', 
            ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'processParameters',
                                    )
        )
                         )

ProductionFilterSequence = cms.Sequence(generator)
