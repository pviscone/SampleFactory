#!/usr/bin/env python3
from datetime import datetime

import json
import configparser
import os, sys
import argparse
import warnings

from scripts.logger import Logger
from scripts.argparser import ArgParser


class SubmitFactory:
    def __init__(self):
        self.nSteps=0
        self.WARNINGS = 0
        self.TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.FACTORY = os.getenv("FACTORY")
        self.MY_NAME = os.getenv("USER")

        self.BASE_OS = []

        self.ARGS = vars(ArgParser(__file__))
        self.__validate_ARGS()

        self.__prepare_JOBS()
        self.__submit_JOBS()

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
        if not os.path.exists(self.ARGS["fragment"]):
            Logger.ERROR(self.ARGS["fragment"] + " does not exist")
        if int(self.ARGS["nevents"]) > 5000:
            Logger.WARNING(self.ARGS["nevents"] + " larger than 5000, jobs might take too long to finish before condor walltime")
        if os.getenv("ProcId"):
            self.PROCID = os.getenv("ProcId")
        else:
            self.PROCID = "0"

    def __validate_JOBS(self, steps, workflows, keeps):
        if set(steps) != set(workflows.keys()) or len(set(steps)) != len(steps):
            # print (steps)
            # print (workflows.keys())
            # Logger.WARNING("STEPS : " + steps)
            # Logger.WARNING("WORKFLOWS : " + workflows.keys())
            Logger.ERROR("Defined STEPS and WORKFLOWS does not agree")
        for k in keeps:
            if not (k in steps):
                # Logger.WARNING("STEPS : " + steps)
                # Logger.WARNING("KEEPS : " + keeps)
                Logger.ERROR("Defined STEPS and KEEPS do not agree")

    def __prepare_JOBS(self):
        chain_json = self.__read_JSON(self.ARGS["chain"])
        steps = chain_json["STEPS"]
        workflows = chain_json["WORKFLOWS"]
        keeps = chain_json["KEEPS"]

        user_json = self.__read_JSON(f"configs/user_{self.MY_NAME}.json")
        self.XROOTD_HOST = user_json["XROOTD_HOST"]
        self.LFN_PATH = user_json["LFN_PATH"]

        self.__validate_JOBS(steps=steps, workflows=workflows, keeps=keeps)

        self.FRAGMENT_NAME = os.path.basename(self.ARGS["fragment"]).split(".")[0]
        self.CHAIN_NAME = os.path.basename(self.ARGS["chain"]).split(".")[0]
        self.JOBDIR = f"{self.FRAGMENT_NAME}/{self.CHAIN_NAME}/{self.TIMESTAMP}"
        self.SUBMITDIR = f"{self.FACTORY}/jobs/{self.JOBDIR}"

        os.system(f"mkdir -p {self.SUBMITDIR}")


        # steps that requires fragments as inputs (root requests)
        req_frags = ["wmLHEGS", "wmLHE", "GS", "wmLHEGEN", "GEN"]
        run_writes_total = ["#!/usr/bin/env bash\n"]
        for wf_idx, (wf, cfg) in enumerate(workflows.items()):
            cmsdriver_writes = []
            run_writes = []
            run_writes.append(f"#!/usr/bin/env bash\n")
            run_writes.append(f"cat /etc/os-release\n")
            run_writes.append("echo 'JOBINDEX ===>' ${PROCID}\n")
            run_writes.append(f"####################################")
            run_writes.append(f"source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
            run_writes.append(f"echo 'STEP {wf_idx} : {wf}'")

            CMSSW_VERSION = cfg["CMSSW_VERSION"]
            SCRAM_ARCH = cfg["SCRAM_ARCH"]
            OPTIONS = cfg["OPTIONS"]
            CUSTOMIZES = cfg["CUSTOMIZES"]  # TODO

            singularity = "cmssw-el"
            if "7" in SCRAM_ARCH.split("_")[0]:
                singularity +="7 -- "
            elif "8" in SCRAM_ARCH.split("_")[0]:
                singularity +="8 -- "
            elif "9" in SCRAM_ARCH.split("_")[0]:
                singularity +="9 -- "
            # append OS for unit test apptainers for now
            # TODO not sure what to do with this for now
            # do we have any campaigns that runs on different OS releases?
            self.BASE_OS.append(SCRAM_ARCH)

            run_writes.append(f"export SCRAM_ARCH={SCRAM_ARCH}")
            run_writes.append(f"cmsrel {CMSSW_VERSION}")
            run_writes.append(f"cd {CMSSW_VERSION}/src")
            run_writes.append(f"cmsenv")
            run_writes.append(f"cd ../..\n")

            give_fragment = any(req_frag in wf for req_frag in req_frags)
            if give_fragment:
                fragment_path = os.path.join("Configuration", "GenProduction", "python")
                run_writes.append(f"mkdir -p {CMSSW_VERSION}/src/{fragment_path}/")
                run_writes.append(f"cp fragment.py {CMSSW_VERSION}/src/{fragment_path}/")
                run_writes.append(f"cd {CMSSW_VERSION}/src")
                run_writes.append(f"scram b")
                run_writes.append(f"cd ../..\n")
                cmsdriver_writes.append(f"{fragment_path}/fragment.py")
                cmsdriver_writes.append(f"-n " + self.ARGS["nevents"])
                cmsdriver_writes.append(
                    f' --customise_commands "from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper; randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService); randSvc.populate();"'
                )
            else:
                cmsdriver_writes.append(f"{wf}")
                cmsdriver_writes.append(f"-n -1")
                previous_wf = list(workflows.keys())[wf_idx - 1]
                cmsdriver_writes.append(f"--filein file:{previous_wf}.root")
            cmsdriver_writes.append(f"--fileout file:{wf}.root")
            cmsdriver_writes.append(f"--python_filename {wf}.py")
            cmsdriver_writes.append(f"--no_exec")
            for opt_name, opt_value in OPTIONS.items():
                if opt_name == "pileup_input":
                    continue
                if opt_value is None:
                    cmsdriver_writes.append(f"--{opt_name}")
                else:
                    cmsdriver_writes.append(f"--{opt_name} {opt_value}")
            if "pileup_input" in OPTIONS.keys():
                if self.ARGS["das_premix"]:
                    cmsdriver_writes.append(f"--pileup_input {OPTIONS['pileup_input']}")
                else:
                    cmsdriver_writes.append(f"--pileup_input filelist:pileup.txt")
                    if not os.path.exists(f"{self.FACTORY}/data/pileups/{self.CHAIN_NAME}.txt"):
                        Logger.ERROR(f"could not find {self.FACTORY}/data/pileups/{self.CHAIN_NAME}.txt")
                    os.system(f"cp {self.FACTORY}/data/pileups/{self.CHAIN_NAME}.txt {self.SUBMITDIR}/pileup.txt")
                # ignore log for premix step as it prints out all pileup_input
                cmsdriver_writes.append("&> /dev/null")

            os.system(f"touch {self.SUBMITDIR}/pileup.txt")  # FIXME stupid hacky line to make NanoGEN work without thinking

            cmsdriver_cmd = "cmsDriver.py"
            for cmsdriver_write in cmsdriver_writes:
                cmsdriver_cmd += f" {cmsdriver_write}"

            run_writes.append(cmsdriver_cmd)
            run_writes.append(f"time cmsRun {wf}.py")
            if "pileup_input" in OPTIONS.keys():
                run_writes.append(f"for ATTEMPT in {{1..10}}; do")
                run_writes.append(f"    if [ -f \"{wf}.root\" ]; then")
                run_writes.append(f"        if ! edmFileUtil -f \"{wf}.root\" &>/dev/null; then")
                run_writes.append(f"            echo SAMPLEFACTORY::{wf}.root is corrupted")
                run_writes.append(f"        else")
                run_writes.append(f"            NEVENTS=$(edmFileUtil -f \"{wf}.root\" | grep -oP '\\(\\d+ runs, \\d+ lumis, \\K\\d+(?= events)')")
                run_writes.append(f"            if [[ -z \"$NEVENTS\" ]]; then")
                run_writes.append(f"                echo SAMPLEFACTORY::Could not parse number of events in {wf}.root")
                run_writes.append(f"            elif (( NEVENTS == 0 )); then")
                run_writes.append(f"                echo SAMPLEFACTORY::{wf}.root has 0 events, likely corrupted")
                run_writes.append(f"            else")
                run_writes.append(f"                echo SAMPLEFACTORY::Finished processing {wf}.root with trials $ATTEMPT")
                run_writes.append(f"                break")
                run_writes.append(f"            fi")
                run_writes.append(f"        fi")
                run_writes.append(f"    fi")
                run_writes.append(f"    echo SAMPLEFACTORY::Could not find valid {wf}.root, resubmitting with trials $ATTEMPT")
                run_writes.append(f"    time cmsRun {wf}.py")
                run_writes.append(f"done")

            run_writes.append(f"####################################\n")
            with open(f"{self.SUBMITDIR}/run_step{wf_idx}.sh", "w") as wf:
                for run_write in run_writes:
                    wf.write(run_write + "\n")
            os.system(f"chmod a+x {self.SUBMITDIR}/run_step{wf_idx}.sh")
            run_writes_total.append(f"{singularity} ./run_step{wf_idx}.sh\n")
            self.nSteps +=1

        run_writes_total.append(f"####################################")
        os.system(f"xrdfs {self.XROOTD_HOST} mkdir -p {self.LFN_PATH}/SampleFactory/{self.JOBDIR}")
        for keep in keeps:
            xrdcp_file = f"{keep}_" + "${PROCID}.root"
            run_writes_total.append(f"echo '{keep}.root will be xrdcped as' {xrdcp_file}")
            run_writes_total.append(f"xrdfs {self.XROOTD_HOST} mkdir -p {self.LFN_PATH}/SampleFactory/{self.JOBDIR}")
            run_writes_total.append(f"xrdcp {keep}.root {self.XROOTD_HOST}/{self.LFN_PATH}/SampleFactory/{self.JOBDIR}/{xrdcp_file}")

        run_writes_total.append("rm *.root")
        with open(f"{self.SUBMITDIR}/run.sh", "w") as wf:
            for run_write in run_writes_total:
                wf.write(run_write + "\n")
        os.system(f"chmod a+x {self.SUBMITDIR}/run.sh")
        
        os.system(f"cp " + self.ARGS["fragment"] + f" {self.SUBMITDIR}/fragment.py")

    def __submit_JOBS(self):
        launching_os = self.BASE_OS[0].split("_")[0]
        if launching_os.endswith("7"):
            os_version = "el7"
        elif launching_os.endswith("8"):
            os_version = "el8"
        elif launching_os.endswith("9"):
            os_version = "el9"

        Logger.INFO("################################")
        Logger.INFO("################################")
        Logger.INFO(f"JOBDIR : jobs/{self.JOBDIR}")
        Logger.INFO(f"XROOTD_HOST : {self.XROOTD_HOST}")
        Logger.INFO(f"LFN_PATH : {self.LFN_PATH}/{self.JOBDIR}")
        # Logger.INFO(f"JOBID : {self.PROCID}")
        Logger.INFO("################################")
        for arg_name, arg_value in self.ARGS.items():
            Logger.INFO(f"{arg_name} : {arg_value}")
        Logger.INFO("################################")
        Logger.INFO("################################")

        os.system(f"cp $(voms-proxy-info --path) {self.SUBMITDIR}/MyProxy")
        os.system(f"cp {self.FACTORY}/data/condor/" + self.ARGS["host"] + f"/condor.jds {self.SUBMITDIR}/")
        os.system(f"sed -i 's|@@JobBatchName@@|{self.FRAGMENT_NAME}__{self.CHAIN_NAME}|g' {self.SUBMITDIR}/condor.jds")
        os.system(f"sed -i 's|@@RequestMemory@@|16000|g' {self.SUBMITDIR}/condor.jds")
        # TODO generalize needed inputs for other use cases
        steps_files=",".join([f"{self.SUBMITDIR}/run_step{idx}.sh" for idx in range(self.nSteps)])
        os.system(f"sed -i 's|@@transfer_input_files@@|{self.SUBMITDIR}/fragment.py,{self.SUBMITDIR}/pileup.txt,{steps_files}|g' {self.SUBMITDIR}/condor.jds")
        os.system(f"sed -i 's|@@SUBMITDIR@@|{self.SUBMITDIR}|g' {self.SUBMITDIR}/condor.jds")
        os.system(f"sed -i 's|@@MyWantOS@@|{os_version}|g' {self.SUBMITDIR}/condor.jds")
        os.system(f"sed -i 's|@@queue@@|" + self.ARGS["njobs"] + f"|g' {self.SUBMITDIR}/condor.jds")

        os.chdir(self.SUBMITDIR)
        if self.ARGS["test"]:
            Logger.INFO(f"Testing the submission script in {self.SUBMITDIR}")
            os.system(f"$(echo {self.SUBMITDIR}/run.sh) > test.log.{self.TIMESTAMP}")
            with open(f"test.log.{self.TIMESTAMP}") as rf:
                if "Traceback" in rf.read():
                    Logger.ERROR(f"Traceback error found in the log file test.log.{self.TIMESTAMP}")
        else:
            os.system(f"condor_submit {self.SUBMITDIR}/condor.jds")
        os.chdir(self.FACTORY)


if __name__ == "__main__":
    SubmitFactory()
