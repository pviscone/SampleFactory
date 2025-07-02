#!/usr/bin/env bash
cmsrel CMSSW_15_1_0_pre4
cd CMSSW_15_1_0_pre4/src
cmsenv
cd ../..
crab submit -c crab.py
