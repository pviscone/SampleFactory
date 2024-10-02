# Release Notes
- 2024/10/01 : v1.0.beta

# Sample Factory

These set of scripts faciliate the production of private MC samples for CMS analyses (and possibly extend to other use cases in the future). Most of it is copy pasted ~~by hand~~ from McM website [link](https://cms-pdmv-prod.web.cern.ch/mcm/) but organized in JSON format for easier maintenance purposes. As there is no automatized way to parse the chains from McM, it needs to be maintained from time to time by hand.

The repository consists of several main parts :

- Chains
- Fragments
- Submitter
- Chain collector (optional)
- Pileup collector (optional)

These will be described with a little more details below.

Keep in mind that the strings in scripts below covered with `$` such as `$THIS$` has to be replaced with user's own configuration.

Comments/feedbacks will be appreciated.
- email : shjeon@NOSPAMcern.ch
- skype : sihyun_jeon

**Also note that sample production might be computationally heavy job. So just becareful when trying to massively produce samples as it can bottleneck the whole server affecting other people's jobs.**

# Running the Sample Factory

## Creating User Configuration

Users should create `configs/user_${USER}.json` configuration file which holds information for the followings :

- XROOTD_HOST : Host name of the XROOTD area where you want your produced samples to be sent to.
- LFN_PATH : Corresponding LFN path in the XROOTD_HOST where you want your produced samples to be sent to.

If you are unsure on what to do, easiest way to start is by copy pasting below to your `configs/user_${USER}.json` as 99.99% of us will have and EOS area in LXPLUS server.

```
{
    "XROOTD_HOST" : "root://eosuser.cern.ch/",
    "LFN_PATH" : "/eos/user/s/simpson"
}
```

I do not have access to most of CMS servers so questions on `XROOTD_HOST` or `LFN_PATH` other than LXPLUS is something that I am not able answer (consult with your server maintenance team).

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
-j 10
```

This submits the `DummyTest` physics process with `Run3Summer22` conditions. If you don't want to care too much about details but rather "I want my physics process samples with `Run3Summer22` condition", just modify `-f` option to the python configuration file that contains your desired physics process and `-n` option and `-j` which ultimately defines your total number of events. In order to run a unit test locally instead of submitting the job through condor, add `--test`.

# Actual Workflow

Note that for normal users who are not so familiar with the production workflow or who does not necessarily have to do something fancy that needs customization, you would not need to change anything in **Chains**. Just taking a look at what **Fragments** and **Submitter** will most likely be enough.

## Chains

`data/chains/` contains the JSON files that is taken from McM and formatted into JSON. It also defines which step of the file will be transferred back (as saving all outputs from all steps, e.g. GEN-SIM, will be huge and not necessary).

- `WORKFLOWS` : Detailed environment settings and options to be given for `cmsDriver.py` to create the python configuration file for each steps. Look at Sequences tab in [link](https://cms-pdmv-prod.web.cern.ch/mcm/requests?member_of_chain=GEN-chain_Run3Summer22wmLHEGS_flowRun3Summer22DRPremix_flowRun3Summer22MiniAODv4_flowRun3Summer22NanoAODv12-00184&page=0&shown=549755814015) as an example. These are all parsed into JSON format with required CMSSW versions.

- `STEPS` : An array that contains the name of each steps defined in `WORKFLOWS`. Simply put, the keys in `WORKFLOWS` have to be exactly agree with what is in `STEPS`.

- `KEEPS` : This defines which step of the output will be kept. For example, if `STEPS` is defined as `["STEP1", "STEP2", "STEP3", "STEP4"]` and `KEEPS` is defined as `["STEP1", "STEP3"]`, outputs from `STEP1` and `STEP3` will only transferred back while the others will be removed after the whole execution finishes.

## Fragments

`data/fragments/` contains the python configuration files that defines the physics process one wants to produce. In case of samples that requires gridpacks, `ExternalLHEProducer` should be written as well. Take a look at `Fragment` tab in [link](https://cms-pdmv-prod.web.cern.ch/mcm/requests?member_of_chain=GEN-chain_Run3Summer22wmLHEGS_flowRun3Summer22DRPremix_flowRun3Summer22MiniAODv4_flowRun3Summer22NanoAODv12-00184&page=0&shown=262271) as an example.

## Submitter

`runFactory.py` is the master processor of the whole workflow.
It has to be given with following arguments :

- `--chain` : Path to the JSON file in `data/chains/`. Defines the campaign and the sample production steps.

- `--fragment` : Path to the python configuration file in `data/fragments`. Defines the physics process to be simulated in the sample production.

- `--nevents` : Number of events to produce per job.

- `--njobs` : Number of jobs to submit. Hence, the sample production will in the end return `nevents x njobs` events in total (assuming there is no failure in jobs, filter, or jet matching/merging involved).

- `--test` : One can test the scripts by giving this option before deploying massive jobs to condor. But try to give small `--nevents` if this is the case as you would probably not want to produce too many events locally.

## Chain Collector

`getChains.py` takes the list of PrepIds as an input defined in JSON format in `data/prepids`. It takes the McM validation script of the given PrepId, parse options for the cmsDriver.py command in a rough text based way, and prepares a JSON file which contains the full production chain information as in the files existing in `data/chains/` repository. You can test it via following command. This is to avoid human error (looking at McM, copying every single option one by one by hand, pasting it in your terminal) and semi-automatically do the work for you. Depending on the development of McM, this might not work as McM validation scripts can evolve throughout time.

```
./getChains.py data/prepids/Run3Summer22.json
```

If you want a new chain that does not exist in this repository or if you want to update the existing ones, you have to navigate through McM (on how to do this, please check [link](https://exo-mc-and-i.gitbook.io/exo-mc-and-interpretation/others/finding-prepids-in-mcm)), pick one sample that is already produced with your desired chain, copy paste the prepids into JSON format and execute `./getChains.py` as above. The output of the script will be given with name `chain_FIRSTPREPID-LASTPREPID.json`. If only one PrepId is given as an input, it will be `chain_FIRSTPREPID.json`. Put this output into `data/chains/` and check if it works!

## Pileup Collector

**NOT UPDATED YET** Function in place `getPileup.py` and working but just missing documentation for now.

# Logs
- 2024/10/01
  - Deploying v1.0.beta
  - Rebased the branch to make it clean
  - Added CI/CD test

- 2024/09/25
  - Added the chain collector to mine the cmsDriver commands from McM validation script
  - Added all 2022 and 2023 campaigns available as of today
  - Added a readme on chain collector

- 2024/09/15
  - Added Run3Summer22wmLHEGS chain.
  - Rebuilt the workflow so that it can run the whole step in one go (before it was tedious/annoying as every single step was treated separately).
  - Deprecated CRAB submission (not sure if I want to revive this) and totally moved to condor.

- Original work started during EXO MC&I convenership for CMS EXO community [link](https://gitlab.cern.ch/cms-exo-mci/EXO-MCsampleProductions/-/tree/master). Also from helpful discussions with Michael Krohn, David Yu, and Sitian Qian.
