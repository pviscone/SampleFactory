#!/usr/bin/env python3
import os
import sys
import json

from scripts.logger import Logger
from scripts.argparser import ArgParser

class CmsDriverCollector:
    def __init__(self, scram_arch):
        self.scram_arch = scram_arch
        self.workflows = {}

    def Run(self, step, prepid):
        def AppendDicts(step, cmssw, l):
            index = 1
            key = step
            while key in self.workflows:
                key = f"{step}Step{index}"
                index += 1
            customizes = {
                "files" : [],
                "pre-cmsRun" : [],
                "post-cmsRun" :[]
            }
            self.workflows[key] = {
                "SCRAM_ARCH" : self.scram_arch,
                "CMSSW_VERSION" : cmssw,
                "OPTIONS" : CmsDriverParser(l),
                "CUSTOMIZES" : customizes
            }

        script_path = f"__{step}.txt"
        mcm_web= "https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_test/"
        os.system(f"wget {mcm_web}/{prepid} -O {script_path}")
        with open(script_path) as openf:
            cmssw = None
            for l in openf:
                l = l.strip()
                if l.startswith("scram p CMSSW "):
                    cmssw = l.split(" ")[-1]
                if l.startswith("cmsDriver.py "):
                    if not cmssw: 
                        Logger.ERROR("parser couldn't find CMSSW version from the script")
                    AppendDicts(step, cmssw, l)
        self.Close(script_path)

    def Close(self, script_path):
        os.system(f"rm {script_path}")

    def Out(self):
        return self.workflows

def CmsDriverParser(line):
    IGNORES = ["python_filename", "customise", "filein", "fileout", "customise_commands", "n", "no_exec"]
    # python_filename, filein, fileout, n, no_exec later gets added through runFactory.py
    options = {}
    line = line.split("||")[0]
    line = line.split("cmsDriver.py")[1]
    args = line.split(" ")
    args.remove("")
    for index, this_arg in enumerate(args):
        if this_arg.startswith("-") and (not this_arg.replace("-", "") in IGNORES):
            next_arg = args[index+1]
            if next_arg.startswith("-"):
                options[this_arg.replace("-", "")] = None
            else:
                if next_arg == "NANOEDMAODSIM":
                    # change EDM NanoAOD to flat NanoAOD
                    next_arg = "NANOAODSIM"
                options[this_arg.replace("-", "")] = next_arg
    return options

def CreateJson(workflows):
    steps = list(workflows.keys())
    chain_name = steps[0]
    chain_name += f"-{steps[-1]}" if len(steps) > 1 else ""
    output = {
        "STEPS" : steps,
        "KEEPS" : [steps[-1]],
        "WORKFLOWS" : workflows
    }
    with open(f"data/chains/chain_{chain_name}.json", "w") as openf:
        json.dump(output, openf, indent=6)
    Logger.INFO(f"json file for {chain_name} created in data/chains")

if __name__ == "__main__":

    json_name = sys.argv[1]

    with open(json_name) as openf:
        data = json.load(openf)

    scram_arch = data["SCRAM_ARCH"]
    collector = CmsDriverCollector(scram_arch)
    for step, config in data["STEPS"].items():
        Logger.INFO(f"preparing step {step}")
        prepid = config["prepid"]
        collector.Run(step, prepid)
    workflows = collector.Out()
    CreateJson(workflows)

