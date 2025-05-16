import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8ConcurrentGeneratorFilter",
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13600.0),
    maxEventsToPrint = cms.untracked.int32(1),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'ExtraDimensionsLED:monojet = on', 
            'ExtraDimensionsLED:CutOffmode = 1', 
            'ExtraDimensionsLED:t = 0.5', 
            'ExtraDimensionsLED:n = 6', 
            'ExtraDimensionsLED:MD = 10000', #scale of gravity in GeV
            'ExtraDimensionsLED:LambdaT = 2000',
            '5000039:m0 = 1200', #5000039 is fixed for monoZ and monojet
            '5000039:mWidth = 1000',
            '5000039:mMin = 1.', 
            '5000039:mMax = 13990.', 
            'PhaseSpace:pTHatMin = 80',
            'PDF:useHard = on',
            'PDF:pHardSet = LHAPDF6:NNPDF23_lo_as_0130_qed',
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings', 
            'pythia8CP5Settings', 
            'processParameters'
        )
    )
)

