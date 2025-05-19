import FWCore.ParameterSet.Config as cms


generator = cms.EDProducer("FlatRandomPtGunProducer",
    PGunParameters = cms.PSet(
        MaxPt = cms.double(100.0),
        MinPt = cms.double(1.0),
        PartID = cms.vint32(22),
        MaxEta = cms.double(3.1),
        MaxPhi = cms.double(3.14159265359),
        MinEta = cms.double(-3.1),
        MinPhi = cms.double(-3.14159265359)
    ),
    Verbosity = cms.untracked.int32(0),
    psethack = cms.string('double photon pt 1 to 100'),
    AddAntiParticle = cms.bool(True),
    firstRun = cms.untracked.uint32(1)
)
