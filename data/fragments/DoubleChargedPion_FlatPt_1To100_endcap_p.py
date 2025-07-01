#TSG-Phase2Spring24GS-00011
#TSG-chain_Phase2Spring24GS_flowPhase2Spring24MiniAODPU200-00003
#/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v2/GEN-SIM-DIGI-RAW-MINIAOD

import FWCore.ParameterSet.Config as cms


generator = cms.EDProducer("FlatRandomPtGunProducer",
    PGunParameters = cms.PSet(
        MaxPt = cms.double(100.0),
        MinPt = cms.double(1.0),
        PartID = cms.vint32(211),
        MaxEta = cms.double(3.),
        MaxPhi = cms.double(3.14159265359),
        MinEta = cms.double(1.479),
        MinPhi = cms.double(-3.14159265359)
    ),
    Verbosity = cms.untracked.int32(0),
    psethack = cms.string('double pion pt 1 to 100'),
    AddAntiParticle = cms.bool(True),
    firstRun = cms.untracked.uint32(1)
)
