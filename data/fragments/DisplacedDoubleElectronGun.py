import FWCore.ParameterSet.Config as cms

generator = cms.EDProducer("FlatRandomPtAndLxyGunProducer",
    PGunParameters = cms.PSet(
        PartID = cms.vint32(11),
        MinPt  = cms.double(0.5),
        MaxPt  = cms.double(40.00),
        MinEta = cms.double(-2.5),
        MaxEta = cms.double(2.5),
        MinPhi = cms.double(-3.14159265359),
        MaxPhi = cms.double(3.14159265359),
        LxyMin = cms.double(0.),
        LxyMax = cms.double(5.0),
        LzMax = cms.double(100.0),
    ),
    Verbosity = cms.untracked.int32(0), ## set to 1 (or greater)  for printouts
    psethack = cms.string('displaced electron'),
    AddAntiParticle = cms.bool(True),
    firstRun = cms.untracked.uint32(1)
)
