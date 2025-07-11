import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8GeneratorFilter",
                                                  comEnergy = cms.double(13000.0),
                                                  crossSection = cms.untracked.double(1),
                                                  filterEfficiency = cms.untracked.double(1),
                                                  maxEventsToPrint = cms.untracked.int32(1),
                                                  pythiaHepMCVerbosity = cms.untracked.bool(False),
                                                  pythiaPylistVerbosity = cms.untracked.int32(1),
                                                  PythiaParameters = cms.PSet(
                                                              pythia8CommonSettingsBlock,
                                                              pythia8CP5SettingsBlock,
                                                              processParameters = cms.vstring(
                                                                              'WeakSingleBoson:ffbar2W = on',
                                                                              '24:onMode = off',
                                                                              '24:onIfAny = 13,14',
                                                                              '24:mMin = 100',
                                                                              '24:mMax = 200'
                                                                              ),
                                                              parameterSets = cms.vstring(
                                                                              'pythia8CommonSettings',
                                                                              'pythia8CP5Settings',
                                                                              'processParameters')
                                                              )
                                                  )
ProductionFilterSequence = cms.Sequence(generator)
