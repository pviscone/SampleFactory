#!/usr/bin/bash

export FACTORY=$(pwd)

if [ ! $CI ]; then
    export CI=false
fi
source ${FACTORY}/scripts/yoda.sh

echo "--- SampleFactory is at $FACTORY"
sleep 2
echo ""

if [ $CI = true ]; then
    export USER="simpson"
fi

if [ ! -e "configs/user_${USER}.json" ]; then
    echo "--- configs/user_${USER}.json is not found!"
    echo "--- Go back to the README instructions"
    sleep 3
    return 0
fi

# MAYBE NOT NEEDED AT ALL BUT POSSIBLY NEEDED FOR SOME PYTHON MODULES
export SYSTEM_RELEASE=`cat /etc/redhat-release`
if [[ $SYSTEM_RELEASE == *"release 7"* ]]; then
    SCRAM_ARCH=slc7_amd64_gcc10
    CMSSW_VERSION=CMSSW_12_6_5
elif [[ $SYSTEM_RELEASE == *"release 8"* ]]; then
    SCRAM_ARCH=el8_amd64_gcc11
    CMSSW_VERSION=CMSSW_13_2_10
elif [[ $SYSTEM_RELEASE == *"release 9"* ]]; then
    SCRAM_ARCH=el9_amd64_gcc12
    CMSSW_VERSION=CMSSW_13_3_3
else
    echo "Unknown OS for SCRAM_ARCH : $SYSTEM_RELEASE"
    return 1
fi

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/cmssw/${CMSSW_VERSION}/src
eval `scram runtime -sh`
cd $FACTORY

if [ $CI = false ]; then
    echo ""
    voms-proxy-init --voms cms --valid 192:00
    echo ""
fi

