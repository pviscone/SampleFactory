import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *
from GeneratorInterface.EvtGenInterface.EvtGenSetting_cff import *

_generator = cms.EDFilter("Pythia8GeneratorFilter",
    pythiaPylistVerbosity = cms.untracked.int32(0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    maxEventsToPrint = cms.untracked.int32(0),
    comEnergy = cms.double(13600.0),
    ExternalDecays = cms.PSet(
        EvtGen130 = cms.untracked.PSet(
            decay_table = cms.string('GeneratorInterface/EvtGenInterface/data/DECAY_2014_NOLONGLIFE.DEC'),
            particle_property_file = cms.FileInPath('GeneratorInterface/EvtGenInterface/data/evt_2014.pdl'),
            list_forced_decays = cms.vstring('MyB+','MyB-'),        
            operates_on_particles = cms.vint32(),
            convertPythiaCodes = cms.untracked.bool(False),
	    user_decay_embedded= cms.vstring(
'#',
'# This is the decay file for the decay B+ -> J/Psi K + -> E+ E- K+',
'#',
'Alias      MyB+        B+',
'Alias      MyB-        B-',
'ChargeConj MyB-        MyB+',
'Alias      MyJpsi      J/psi',
'ChargeConj MyJpsi      MyJpsi',
'#',
'Decay MyB+',
'  1.000    MyJpsi      K+             SVS;',
'Enddecay',
'CDecay MyB-',
'#',
'Decay MyJpsi',
'  1.000         e+       e-         PHOTOS VLL;',
'Enddecay',
'#',
'End',
	    ),
        ),
        parameterSets = cms.vstring('EvtGen130')
    ),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        #pythia8PSweightsSettingsBlock,
        processParameters = cms.vstring(
            'SoftQCD:nonDiffractive = on',
            'PTFilter:filter = on', # this turn on the filter
            'PTFilter:quarkToFilter = 5', # PDG id of q quark
            'PTFilter:scaleToFilter = 1.0'
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CP5Settings',
            #'pythia8PSweightsSettings',
            'processParameters',
        ),
    )
)
_generator.PythiaParameters.processParameters.extend(EvtGenExtraParticles)
from GeneratorInterface.Core.ExternalGeneratorFilter import ExternalGeneratorFilter
generator = ExternalGeneratorFilter(_generator)

###### Filters ##########

bufilter = cms.EDFilter(
    "PythiaFilter",
    MaxEta = cms.untracked.double(9999.),
    MinEta = cms.untracked.double(-9999.),
    ParticleID = cms.untracked.int32(521) ## Bu
    )

decayfilterpositiveleg = cms.EDFilter(
    "PythiaDauVFilter",
    verbose         = cms.untracked.int32(1),
    NumberDaughters = cms.untracked.int32(2),
    ParticleID      = cms.untracked.int32(521),  ## Bu
    DaughterIDs     = cms.untracked.vint32(443, 321), ## J/psi and K+
    MinPt           = cms.untracked.vdouble(-1., 0.5),
    MinEta          = cms.untracked.vdouble(-9999., -2.5),
    MaxEta          = cms.untracked.vdouble( 9999.,  2.5)
    )

jpsifilter = cms.EDFilter(
    "PythiaDauVFilter",
    verbose         = cms.untracked.int32(1), 
    NumberDaughters = cms.untracked.int32(2), 
    MotherID        = cms.untracked.int32(521),  
    ParticleID      = cms.untracked.int32(443),  
    DaughterIDs     = cms.untracked.vint32(11, -11),
    MinPt           = cms.untracked.vdouble(3.0, 3.0),
    MinEta          = cms.untracked.vdouble(-2.5, -2.5),
    MaxEta          = cms.untracked.vdouble(2.5, 2.5)
    )

ProductionFilterSequence = cms.Sequence(generator+bufilter+decayfilterpositiveleg+jpsifilter)
