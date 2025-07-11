# Sample Factory

These set of scripts facilitate the production of private MC samples for CMS analyses (and possibly extend to other use cases in the future). Most of it is copy pasted ~~by hand~~ from McM website [link](https://cms-pdmv-prod.web.cern.ch/mcm/) but organized in JSON format for easier maintenance purposes. As there is no automatized way to parse the chains from McM, it needs to be maintained from time to time by hand.

The repository consists of several main parts :

- Chains
- Fragments
- Submitter
- Chain collector (optional)
- Pileup collector (optional)

These will be described with a little more details below.

Keep in mind that the strings in scripts below covered with `$` such as `$THIS$` has to be replaced with user's own configuration.

**Also note that sample production might be computationally heavy job. So just be careful when trying to massively produce samples as it can bottleneck the whole server affecting other people's jobs.**

# Running the Sample Factory

## Creating User Configuration

Users should create `configs/user_${USER}.json` configuration file which holds information for the followings :

- XROOTD_HOST : Host name of the XROOTD area where you want your produced samples to be sent to.
- LFN_PATH : Corresponding LFN path in the XROOTD_HOST where you want your produced samples to be sent to.

If you are unsure on what to do, easiest way to start is by copy pasting below to your `configs/user_${USER}.json` as 99.99% of us will have and EOS area in LXPLUS server.

```
{
    "AccountingGroup": "group_u_CMST3.all",
    "XROOTD_HOST" : "root://eoscms.cern.ch/",
    "LFN_PATH" : "/eos/cms/store/cmst3/group/l1tr/pviscone",
    "CRAB_SITE": "T2_CH_CERN",
    "CRAB_PATH": "/store/group/cmst3/group/l1tr/pviscone",
    "git_username": "pviscone",
    "git_name": "Piero Viscone",
    "git_mail": "piero.viscone@cern.ch"
}
```

If you want to run the submission on HTCondor you can setup
- AccountingGroup: Your accounting group (Optional, if you don't have one just remove the field)
- XROOTD_HOST: The EOS XRootD host were you want to copy your output files
- LFN_PATH : The EOS XRootD path were you want to copy your output files

If you want to run the submission on CRAB:
- CRAB_SITE: Where to copy your output files
- CRAB_PATH: Path in the CRAB_SITE where to copy your output files
- git_username, git_name, git_mail : Some git functionalities may need to configure git on the crab machine. To allow this you can put your git info here

## Environment Setup

Next, you should set up the environment by doing below.

```
source setup.sh
```

This does not do something that's very much meaningful, just takes available CMSSW versions in `el7`, `el8`, or `el9` for some basic python modules. Actual sample production jobs will run under the OS environments as defined in McM, this is just for python module/version purposes. So whatever environment you are running these scripts right now does not matter.

## Producing Dummy Samples

You can simply trigger a dummy example to see how it works.

```
./runFactory.py \
-c data/chains/chain_Run3Summer22wmLHEGS-Run3Summer22NanoAODv12.json \
-f data/fragments/DummyTest_TuneCP5_13p6TeV_madgraph-pythia8.py \
-n 20 \
-j 10 \
--das_premix \ # Please read below "Pileup Collector" to avoid using this
```

This submits the `DummyTest` physics process with `Run3Summer22` conditions. If you don't want to care too much about details but rather "I want my physics process samples with `Run3Summer22` condition", just modify `-f` option to the python configuration file that contains your desired physics process and `-n` option and `-j` which ultimately defines your total number of events. In order to run a unit test locally instead of submitting the job through condor, add `--test`.

# Actual Workflow

Note that for normal users who are not so familiar with the production workflow or who does not necessarily have to do something fancy that needs customization, you would not need to change anything in **Chains**. Just taking a look at what **Fragments** and **Submitter** will most likely be enough.

## Chains

`data/chains/` contains the JSON files that is taken from McM and formatted into JSON. It also defines which step of the file will be transferred back (as saving all outputs from all steps, e.g. GEN-SIM, will be huge and not necessary).

- `WORKFLOWS` : Detailed environment settings and options to be given for `cmsDriver.py` to create the python configuration file for each steps. Look at Sequences tab in [link](https://cms-pdmv-prod.web.cern.ch/mcm/requests?member_of_chain=GEN-chain_Run3Summer22wmLHEGS_flowRun3Summer22DRPremix_flowRun3Summer22MiniAODv4_flowRun3Summer22NanoAODv12-00184&page=0&shown=549755814015) as an example. These are all parsed into JSON format with required CMSSW versions.

- `STEPS` : An array that contains the name of each steps defined in `WORKFLOWS`. Simply put, the keys in `WORKFLOWS` have to be exactly agree with what is in `STEPS`.

- `KEEPS` : This defines which step of the output will be kept. For example, if `STEPS` is defined as `["STEP1", "STEP2", "STEP3", "STEP4"]` and `KEEPS` is defined as `["STEP1", "STEP3"]`, outputs from `STEP1` and `STEP3` will only transferred back while the others will be removed after the whole execution finishes.

- `FILES` : If you need to transfer some files to the worker node, you can add it here

### Customization
You can customize your step before running it

In `CUSTOMIZES` you have 3 options:
- `cmssw`: list of commands that runs after `cmsenv` but before `scram b` in the `src` directory of the CMSSW release
- `pre-cmsRun`: list of commands to run in the root of the worker node after the setup of the CMSSW release but before running the `cmsDriver.py` command.
- `post-cmsRun`: list of commands to run in the root of the worker node at the end of the `cmsDriver.py` command.
- `keep`: (default=True) By default all the CMSSW are kept on disk but if you want to save space you can delete a release after the end of the workflow step setting up `"keep": false`

N.B 
1. `OPTION` is optional, if it's not defined no `cmsDriver` command will be run. This is useful if you have a custom CMSSW package and you want to run a script with `cmsRun`. (You have to setup your release in `cmssw` and then insert the `cmsRun` command in `post-cmsRun`
2. If no `CMSSW_VERSION` is set up, no release will be `cmsrel`led. (But `CMSSW_BASE` will still point to the release used in the previous step)

## Fragments

`data/fragments/` contains the python configuration files that defines the physics process one wants to produce. In case of samples that requires gridpacks, `ExternalLHEProducer` should be written as well. Take a look at `Fragment` tab in [link](https://cms-pdmv-prod.web.cern.ch/mcm/requests?member_of_chain=GEN-chain_Run3Summer22wmLHEGS_flowRun3Summer22DRPremix_flowRun3Summer22MiniAODv4_flowRun3Summer22NanoAODv12-00184&page=0&shown=262271) as an example.

## Submitter

`runFactory.py` is the master processor of the whole workflow.
It has to be given with following arguments :

- `--chain` : Path to the JSON file in `data/chains/`. Defines the campaign and the sample production steps.

- `--fragment` : Path to the python configuration file in `data/fragments`. Defines the physics process to be simulated in the sample production.

- `--nevents` : Number of events to produce per job.

- `--njobs` : Number of jobs to submit. Hence, the sample production will in the end return `nevents x njobs` events in total (assuming there is no failure in jobs, filter, or jet matching/merging involved).

- `--crab` : Enable crab submission

- `--memory (int)` : memory assign to each job

- `--flavor` : (For HTCondor submission only) Flavour of the job

- `--test` : One can test the scripts by giving this option before deploying massive jobs to condor. But try to give small `--nevents` if this is the case as you would probably not want to produce too many events locally. (Together with `--crab`, it will run `crab submit --dry-run`)

## Chain Collector

`getChains.py` takes the list of PrepIds as an input defined in JSON format in `data/prepids`. It takes the McM validation script of the given PrepId, parse options for the cmsDriver.py command in a rough text based way, and prepares a JSON file which contains the full production chain information as in the files existing in `data/chains/` repository. You can test it via following command. This is to avoid human error (looking at McM, copying every single option one by one by hand, pasting it in your terminal) and semi-automatically do the work for you. Depending on the development of McM, this might not work as McM validation scripts can evolve throughout time (and please let me know if that is the case!).

```
./getChains.py data/prepids/Run3Summer22wmLHEGS-Run3Summer22NanoAODv12.json
```

If you want a new chain that does not exist in this repository or if you want to update the existing ones, you have to navigate through McM (on how to do this, please check [link](https://exo-mc-and-i.gitbook.io/exo-mc-and-interpretation/others/finding-prepids-in-mcm)), pick one sample that is already produced with your desired chain, copy paste the prepids into JSON format and execute `./getChains.py` as above. The output of the script will be given with name `chain_FIRSTPREPID-LASTPREPID.json`. If only one PrepId is given as an input, it will be `chain_FIRSTPREPID.json`. Put this output into `data/chains/` and check if it works!

## Pileup Collector

Instead of querying the MinBias library for every single job separately (this is also error prone as some of the files get hidden into the tapes from time to time depending on the available storage for the whole CMS), precollect the list and pass the avaialble ones at site to be given as an input to the jobs. Note that this takes quite a long time as it queries multiple T2/T3 sites.

```
./getPileup.py -c data/chains/chain_Run3Summer22wmLHEGS-Run3Summer22NanoAODv12.json
```

If you do not want to do this, keep in mind that you should always give `--das_premix` when executing `runFactory.py`, otherwise it will be empty with MinBias. But as said above, this will take longer time for the jobs to finish so it's better to collect the list earlier and avoid using `--das_premix`.

# Credits
Original work from Sihyun Jeon, initially started during EXO MC&I convenership for CMS EXO community [link](https://gitlab.cern.ch/cms-exo-mci/EXO-MCsampleProductions/-/tree/master). Also from helpful discussions with Michael Krohn, David Yu, and Sitian Qian.
