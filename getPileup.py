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
        os.system(f"dasgoclient -query='file dataset={pileup_dataset}' > data/pileups/{pileup_txt}")

if __name__ == "__main__":
    GetPileup()
