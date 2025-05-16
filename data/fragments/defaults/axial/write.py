import os

samples = {
    "monojet" : [
        "DMSimp_monojet_Axial_GQ-0p25_GDM-1p0_MY1-1000_MXd-10",
        "DMSimp_monojet_Axial_GQ-0p25_GDM-1p0_MY1-2000_MXd-10",
        "DMSimp_monojet_Axial_GQ-0p25_GDM-1p0_MY1-2000_MXd-900",
        "DMSimp_monojet_Axial_GQ-0p25_GDM-1p0_MY1-2500_MXd-10"
    ],
    "monov" : [
        "DMSimp_monov_Axial_GQ-0p25_GDM-1p0_MY1-1000_MXd-10",
        "DMSimp_monov_Axial_GQ-0p25_GDM-1p0_MY1-2000_MXd-10",
        "DMSimp_monov_Axial_GQ-0p25_GDM-1p0_MY1-2000_MXd-900",
        "DMSimp_monov_Axial_GQ-0p25_GDM-1p0_MY1-2500_MXd-10"
    ]
}

for type, sample_ in samples.items():
    for sample in sample_:
        os.system(f"cp base/{type}.py {sample}.py")
        os.system(f"sed -i 's|@@NAME@@|{sample}|g' {sample}.py")
