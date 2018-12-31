#! /usr/bin/env python
"""
    Search and submit all slurm files inside direct subdirectories under
    the given path.
"""

from sys import argv, exit
from os import path, listdir

# check for existing saved_configs.py file
if path.exists("saved_configs.py"):
    # use saved config file
    import saved_configs
    targetWorkingDirectory = saved_configs.iEbeConfigs["working_folder"]
else:
    # use CML arguments
    if len(argv)>=2:
        targetWorkingDirectory = path.abspath(argv[1])
    else:
        targetWorkingDirectory = "PlayGround"

# check existence of target working directory
if path.exists(targetWorkingDirectory):
    print("Start submitting jobs from %s..." % targetWorkingDirectory)
else:
    print("Usage: submitJobs [from_directory=PlayGround]")
    exit()

from subprocess import call

for mainentry in listdir(targetWorkingDirectory):
    subFolder = path.join(targetWorkingDirectory, mainentry)
    if path.isdir(subFolder) :
        for aFile in listdir(subFolder):
            if path.splitext(aFile)[1].lower() == '.slurm':
                commandString = "sbatch %s" % aFile
                print("Submitting %s in %s..." % (aFile, subFolder))
                call(commandString, shell=True, cwd=subFolder)
    else :
        if path.splitext(mainentry)[1].lower() == '.slurm':
            commandString = "sbatch %s" % mainentry
            print("Submitting %s in %s..." % (mainentry, targetWorkingDirectory))
            call(commandString, shell=True, cwd=targetWorkingDirectory)
        

print("Job submission done. See RunRecord.txt file in each job folder for progress.")

