#! /usr/bin/env python
"""
    This script duplicates the EBE-Node folder and generate a collection of pbs
    files to be batch-submitted. For efficiency all codes inside EBE-Node should
    be compiled.
"""

from sys import argv, exit
from os import makedirs, path, unlink, chmod
from shutil import copytree, copy, rmtree
from subprocess import call

from check_prerequisites import checkEnvironment, checkExecutables, greetings

# check argv
try:
    # set parameters
    numberOfJobs = int(argv[1])
    numberOfEventsPerJob = int(argv[2])

    # set optional parameters
    argId = 2

    argId += 1
    if len(argv)>=argId+1: # set working folder
        workingFolder = path.abspath(argv[argId])
    else:
        workingFolder = path.abspath("./PlayGround")

    argId += 1
    if len(argv)>=argId+1: # folder to store results
        resultsFolder = path.abspath(argv[argId])
    else:
        resultsFolder = path.abspath("./RESULTS")

    argId += 1
    if len(argv)>=argId+1: # set wall time
        walltime = argv[argId]
    else:
        walltime = "%02d:00:00" % (1*numberOfEventsPerJob) # 1 hours per job

    argId += 1
    if len(argv)>=argId+1: # whether to compress final results folder
        compressResultsFolderAnswer = argv[argId]
    else:
        compressResultsFolderAnswer = "yes"
except:
    print('Usage: generateJobs.py number_of_jobs number_of_events_per_job [working_folder="./PlayGround"] [results_folder="./RESULTS"] [walltime="03:00:00" (per event)] [compress_results_folder="yes"]')
    exit()

# save config files
open("saved_configs.py", "w").writelines("""
iEbeConfigs = {
    "number_of_jobs"            :   %d,
    "number_of_events_per_job"  :   %d,
    "working_folder"            :   "%s",
    "results_folder"            :   "%s",
    "walltime"                  :   "%s",
    "compress_results_folder"   :   "%s",
}
""" % (numberOfJobs, numberOfEventsPerJob, workingFolder, resultsFolder, walltime, compressResultsFolderAnswer)
)

# define colors
purple = "\033[95m"
green = "\033[92m"
blue = "\033[94m"
yellow = "\033[93m"
red = "\033[91m"
normal = "\033[0m"

# print welcome message
print(yellow)
greetings(3)
print(purple + "\n" + "-"*80 + "\n>>>>> Welcome to the event generator! <<<<<\n" + "-"*80 + normal)

# check prerequisites
print(green + "\n>>>>> Checking for required libraries <<<<<\n" + normal)
if not checkEnvironment():
    print("Prerequisites not met. Install the required library first please. Aborting.")
    exit()

# check existence of executables
print(green + "\n>>>>> Checking for existence of executables <<<<<\n" + normal)
if not checkExecutables():
    print("Not all executables can be generated. Aborting.")
    exit()

# clean up check_prerequisites.pyc
if path.exists("check_prerequisites.pyc"): unlink("check_prerequisites.pyc")

# generate events
print(green + "\n>>>>> Generating events <<<<<\n" + normal)

# prepare directories
if not path.exists(resultsFolder): makedirs(resultsFolder)
if path.exists(workingFolder): rmtree(workingFolder)
makedirs(workingFolder)

ebeNodeFolder = "EBE-Node"
crankFolderName = "crank"
crankFolder = path.join(ebeNodeFolder, crankFolderName)

# copy parameter file into the crank folder
copy("ParameterDict.py", crankFolder)
copy("InitialConditions.py",crankFolder)

# backup parameter files to the result folder
copy(path.join(crankFolder, "SequentialEventDriver.py"), resultsFolder)
copy(path.join(crankFolder, "ParameterDict.py"), resultsFolder)

# duplicate EBE-Node folder to working directory, write .pbs file
for i in range(1, numberOfJobs+1):
    targetWorkingFolder = path.join(workingFolder, "job-%d" % i)
    # copy folder
    copytree(ebeNodeFolder, targetWorkingFolder)

open(path.join(workingFolder, "jobs.slurm"), "w").write(
"""#!/bin/bash
sbatch --job-name=iEBE-array --time=00:10:00 --workdir=%s -- %s/jobs.sh
""" % (workingFolder,workingFolder)
)
chmod(path.join(workingFolder, "jobs.slurm"),0o755)

open(path.join(workingFolder, "jobs.sh"), "w").write(
"""#!/bin/bash
NJOBS=%d
NEVTPERJOB=%d
WORKDIRBASE=%s
TIME=%s

CMD="sbatch -J iEBE-batch --array=1-$NJOBS --workdir=$WORKDIRBASE --time=$TIME -- $WORKDIRBASE/job.sh %s $NEVTPERJOB %s"
JobID=($(eval $CMD | tee | awk '{print $4}'))
""" % (numberOfJobs, numberOfEventsPerJob, workingFolder, walltime, crankFolderName, resultsFolder)
)
chmod(path.join(workingFolder, "jobs.sh"),0o755)


open(path.join(workingFolder, "job.sh"), "w").write(
"""#!/bin/bash
CRANKFOLDER=$1
NEVTPERJOB=$2
RESULTSFOLDER=$3

source /etc/profile.d/modules.sh
module use /cvmfs/it.gsi.de/modulefiles/
module load root/v5-34-14
export ROOTSYS=/cvmfs/it.gsi.de/root/v5-34-14
export QMDUSER=$(whoami)

(cd job-$SLURM_ARRAY_TASK_ID
    (cd $CRANKFOLDER
        ulimit -n 1000
        python ./SequentialEventDriver_shell.py $NEVTPERJOB 1> RunRecord.txt 2> ErrorRecord.txt
        cp RunRecord.txt ErrorRecord.txt ../finalResults/
    )
    (cd ./finalResults
        root -b -q -l "/lustre/nyx/alice/users/$QMDUSER/UrQMDparser/runUrQMDParser.C(\\\"$QMDUSER\\\",\\\"urqmdCombined.txt\\\", $SLURM_ARRAY_TASK_ID)"
        mv UrQMD_output_$SLURM_ARRAY_TASK_ID.root $RESULTSFOLDER
        rm urqmdCombined.txt
    )
    mv ./finalResults $RESULTSFOLDER/job-$SLURM_ARRAY_TASK_ID
)
rm -r job-$SLURM_ARRAY_TASK_ID
""" 
)
if compressResultsFolderAnswer == "yes":
    open(path.join(workingFolder, "job.sh"), "a").write(
"""
(cd $RESULTSFOLDER
    zip -r -m -q job-$SLURM_ARRAY_TASK_ID.zip job-$SLURM_ARRAY_TASK_ID
)
"""
    )
chmod(path.join(workingFolder, "job.sh"),0o755)

# add a data collector watcher
if compressResultsFolderAnswer == "yes":
    EbeCollectorFolder = "EbeCollector"
    utilitiesFolder = "utilities"
    watcherFolder = "watcher"
    watcherDirectory = path.join(workingFolder, "watcher")
    makedirs(path.join(watcherDirectory, ebeNodeFolder))
    copytree(path.join(ebeNodeFolder, EbeCollectorFolder), path.join(watcherDirectory, ebeNodeFolder, EbeCollectorFolder))
    copytree(utilitiesFolder, path.join(watcherDirectory, utilitiesFolder))
    open(path.join(workingFolder, "jobs.sh"), "a").write(
"""
    sbatch -J watcher -d afterany:$JobID --time=%s --workdir=%s -- %s/watcher.sh %s %s %s %d
""" % (walltime, workingFolder, workingFolder, watcherFolder, utilitiesFolder, resultsFolder, numberOfJobs)
    )

    open(path.join(workingFolder, "watcher.sh"), "w").write(
"""#!/bin/bash
WATCHERFOLDER=$1
UTILITIESFOLDER=$2
RESULTSFOLDER=$3
NUMBEROFJOBS=$4
(cd $WATCHERFOLDER
    (cd $UTILITIESFOLDER
        python autoZippedResultsCombiner.py $RESULTSFOLDER $NUMBEROFJOBS "job-(\d*).zip" 60 1> WatcherReport.txt 2> WatcherReport.txt
        mv WatcherReport.txt $RESULTSFOLDER
    )
)
rm -r $WATCHERFOLDER
""" 
    )
    chmod(path.join(workingFolder, "watcher.sh"),0o755)


import ParameterDict
import random
initial_condition_type = (
    ParameterDict.initial_condition_control['initial_condition_type'])
if initial_condition_type == 'pre-generated':
    read_in_mode = ParameterDict.initial_condition_control['pre-generated_initial_file_read_in_mode']
    initial_file_path = (ParameterDict.initial_condition_control[
                             'pre-generated_initial_file_path'])
    if read_in_mode == 3 : # IP MUSIC events
        file_pattern = ParameterDict.initial_condition_control['pre-generated_initial_file_pattern']
        head_file_pattern = file_pattern.split('[')[0]
        trail_file_pattern = file_pattern.split('[')[1].split(']')[1]
        total_nevents = int(file_pattern.split('[')[1].split(']')[0].split('-')[1])
        nevents = random.sample(xrange(total_nevents),numberOfJobs*numberOfEventsPerJob)
        for jobno in range(numberOfJobs) :
            targetInitialConditionsFolder = path.join(workingFolder, "job-%d" % (jobno+1), "initial_conditions")
            makedirs(targetInitialConditionsFolder)
            for eventno in range(numberOfEventsPerJob) :
                copy('%s/PbPb%s/%s%d%s' 
                     % (initial_file_path,
                        ParameterDict.initial_condition_control['centrality'].split('%')[0],
                        head_file_pattern,
                        nevents[jobno*numberOfEventsPerJob+eventno]+1,
                        trail_file_pattern),targetInitialConditionsFolder)
    else :
        call("./copy_pre_generated_initial_conditions.sh %d %d %s %s" 
             % (numberOfJobs, numberOfEventsPerJob, initial_file_path,
                workingFolder), shell=True)

print("Jobs generated. Submit them using submitJobs scripts.")



###########################################################################
# 05-23-2013:
#   Bugfix: "cd %s" added to the pbs files.
