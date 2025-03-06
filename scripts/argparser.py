import os
import argparse

def ArgParser(file_name):

    file_name = os.path.basename(file_name)
    if (file_name == "getPileup.py"):
        required_chain = True
        required_fragment = False
        required_nevents = False
        required_njobs = False
    else:
        required_chain = True 
        required_fragment = True
        required_nevents = True
        required_njobs = True

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--chain", required=required_chain, type=str,
                        help="Campaign chain to use for sample production"
                        )
    parser.add_argument("-f", "--fragment", required=required_fragment, type=str,
                        help="Fragment file to use for sample production"
                        )
    parser.add_argument("-n", "--nevents", required=required_nevents, type=str,
                        help="Number of events to submit per job"
                        )
    parser.add_argument("-j", "--njobs", required=required_njobs, type=str,
                        help="Number of jobs to submit"
                        )
    parser.add_argument("--host", required=False, type=str, default="",
                        help="Name of the hosting server"
                        )
    parser.add_argument("--test", required=False, action="store_true", default=False)
    parser.add_argument("--condor_log", required=False, action="store_true", default=False)
    parser.add_argument("--force", required=False, action="store_true", default=False) # FIXME forgot the use case for now
    parser.add_argument("--das_premix", required=False, action="store_true", default=False)

    args = parser.parse_args()

    if args.host == "":
        this_host = os.getenv("HOSTNAME")
        if "login.uscms.org" in this_host:
            args.host = "cmsconnect"
        elif "lxplus" in this_host:
            args.host = "lxplus"
        else:
            args.host = "base"
    return args

