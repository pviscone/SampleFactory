#!/usr/bin/env python3
from datetime import datetime

import json
import configparser
import os, sys
import argparse
import warnings

from scripts.logger import Logger
from scripts.argparser import ArgParser

class GetPileup:
    def __init__(self):
        self.TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.SAMPLEFACTORY = os.getcwd() #os.getenv("SAMPLEFACTORY")

        self.ARGS = vars(ArgParser(__file__))
        self.__validate_ARGS()

        self.__query_DAS()

    def __read_JSON(self, json_file):
        out = None
        with open(json_file) as rf:
            out = json.load(rf)
        if not out:
            Logger.ERROR(json_file + " is empty")
        return out

    def __validate_ARGS(self):
        if not os.path.exists(self.ARGS["chain"]):
            Logger.ERROR(self.ARGS["chain"] + " does not exist")

    def __query_DAS(self):
        self.CHAIN_NAME = os.path.basename(self.ARGS["chain"]).split(".")[0]

        chain_json = self.__read_JSON(self.ARGS["chain"])
        workflows = chain_json["WORKFLOWS"]
        req_frags = ["DRPremix"]
        pileup_dataset = []
        for wf_idx, (wf, cfg) in enumerate(workflows.items()):
            OPTIONS = cfg["OPTIONS"]

            for opt_name, opt_value in OPTIONS.items():
                if opt_name == "pileup_input":
                    pileup_dataset.append(opt_value)

        if len(pileup_dataset) != 1:
            Logger.ERROR("pileup_input not properly not given in " + self.ARGS["chain"])

        pileup_dataset = pileup_dataset[0].replace("dbs:", "").replace("\"","")
        pileup_txt = f"{self.CHAIN_NAME}.txt"
        sites = ["T1_DE_KIT_Disk", "T1_ES_PIC_Disk", "T1_FR_CCIN2P3_Disk", "T1_IT_CNAF_Disk", "T1_UK_RAL_Disk", "T1_US_FNAL_Disk", "T2_AT_Vienna", "T2_BE_IIHE", "T2_BE_UCL", "T2_CH_CERN", "T2_CH_CSCS", "T2_DE_DESY", "T2_DE_RWTH", "T2_ES_CIEMAT", "T2_ES_IFCA", "T2_FR_GRIF", "T2_FR_IPHC", "T2_IT_Bari", "T2_IT_Legnaro", "T2_IT_Pisa", "T2_IT_Rome", "T2_UK_London_Brunel", "T2_UK_London_IC", "T2_UK_SGrid_RALPP", "T2_US_Caltech", "T2_US_Florida", "T2_US_MIT", "T2_US_Nebraska", "T2_US_Purdue", "T2_US_UCSD", "T2_US_Vanderbilt", "T2_US_Wisconsin"]
        if os.path.exists(f"data/pileups/{pileup_txt}"):
            os.system(f"rm data/pileups/{pileup_txt}")
        os.system(f"touch data/pileups/{pileup_txt}")
        for site in sites:
            Logger.WARNING(f"checking {pileup_dataset} in {site}")
            #print (f"dasgoclient -query='file dataset={pileup_dataset} site={site}'")
            os.system(f"dasgoclient -query='file dataset={pileup_dataset} site={site}' >> data/pileups/{pileup_txt}")
            os.system(f"sort data/pileups/{pileup_txt} > data/pileups/__{pileup_txt}")
            os.system(f"uniq data/pileups/__{pileup_txt} > data/pileups/{pileup_txt}")
            os.system(f"rm data/pileups/__{pileup_txt}")
        with open(f"data/pileups/{pileup_txt}") as rf:
            nfiles = len(rf.readlines())
            Logger.INFO(f"collected {nfiles} files for {pileup_dataset}")
            if nfiles == 0:
                Logger.WARNING(f"wasn't able to collect any files for {pileup_dataset}")
                Logger.WARNING(f"querying DAS for full dataset")
                os.system(f"dasgoclient -query='file dataset={pileup_dataset}' > data/pileups/{pileup_txt}")

if __name__ == "__main__":
    GetPileup()
