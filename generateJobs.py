#! /usr/bin/env python
"""
    This script duplicates the EBE-Node folder and generate a collection of pbs
    files to be batch-submitted. For efficiency all codes inside EBE-Node should
    be compiled.
"""

from sys import argv, exit
from os import makedirs, path
from shutil import copytree, copy, rmtree

from check_prerequisites import checkEnvironment, checkExecutables

# check argv
try:
    # set parameters
    numberOfJobs = int(argv[1])
    numberOfEventsPerJob = int(argv[2])

    # set optional parameters
    if len(argv)>=4: # folder to store results
        resultsFolder = path.abspath(argv[3])
    else:
        resultsFolder = path.abspath("./RESULTS")

    if len(argv)>=5: # set wall time
        walltime = argv[4]
    else:
        walltime = "30:00:00"

    if len(argv)>=6: # set working folder
        workingFolder = path.abspath(argv[5])
    else:
        workingFolder = path.abspath("./PlayGround")

    if len(argv)>=7: # whether to compress final results folder
        compressResultsFolderAnswer = argv[6]
    else:
        compressResultsFolderAnswer = "yes"
except:
    print('Usage: generateJobs.py number_of_jobs number_of_events_per_job [results_folder="./RESULTS"] [walltime="03:00:00"] [working_folder="./PlayGround"] [compress_results_folder="yes"]')
    exit()

# check prerequisites
print("\n>>>>> Checking required libraries <<<<<\n")
if not checkEnvironment():
    print("Prerequisites not met. Install the required library first please. Aborting.")
    exit()

# check existence of executables
print("\n>>>>> Checking existence of executables <<<<<\n")
if not checkExecutables():
    print("Not all executables can be generated. Aborting.")
    exit()

# generate events
print("\n>>>>> Generating events <<<<<\n")

# prepare directories
if not path.exists(resultsFolder): makedirs(resultsFolder)
if path.exists(workingFolder): rmtree(workingFolder)
makedirs(workingFolder)

ebeNodeFolder = "EBE-Node"
crankFolderName = "crank"
crankFolder = path.join(ebeNodeFolder, crankFolderName)

# copy parameter file into the crank folder
copy("ParameterDict.py", crankFolder)

# backup parameter files to the result folder
copy(path.join(crankFolder, "SequentialEventDriver.py"), resultsFolder)
copy(path.join(crankFolder, "ParameterDict.py"), resultsFolder)

# duplicate EBE-Node folder to working directory, write .pbs file
for i in range(1, numberOfJobs+1):
    targetWorkingFolder = path.join(workingFolder, "job-%d" % i)
    # copy folder
    copytree(ebeNodeFolder, targetWorkingFolder)
    open(path.join(targetWorkingFolder, "job-%d.pbs" % i), "w").write(
"""
#!/usr/bin/env bash
#PBS -N iEBE-%d
#PBS -l walltime=%s
#PBS -j oe
#PBS -S /bin/bash
(cd %s
    ulimit -n 1000
    python ./SequentialEventDriver_shell.py %d 1> RunRecord.txt 2> ErrorRecord.txt
    cp RunRecord.txt ErrorRecord.txt ../finalResults/
)
mv ./finalResults %s/job-%d
""" % (i, walltime, crankFolderName, numberOfEventsPerJob, resultsFolder, i)
    )
    if compressResultsFolderAnswer == "yes":
        open(path.join(targetWorkingFolder, "job-%d.pbs" % i), "a").write(
"""
(cd %s
    zip -r -m -q job-%d.zip job-%d
)
""" % (resultsFolder, i, i)
        )

# add a data collector watcher
if compressResultsFolderAnswer == "yes":
    EbeCollectorFolder = "EbeCollector"
    utilitiesFolder = "utilities"
    watcherDirectory = path.join(workingFolder, "watcher")
    makedirs(path.join(watcherDirectory, ebeNodeFolder))
    copytree(path.join(ebeNodeFolder, EbeCollectorFolder), path.join(watcherDirectory, ebeNodeFolder, EbeCollectorFolder))
    copytree(utilitiesFolder, path.join(watcherDirectory, utilitiesFolder))
    open(path.join(watcherDirectory, "watcher.pbs"), "w").write(
"""
#!/usr/bin/env bash
#PBS -N watcher
#PBS -l walltime=%s
#PBS -j oe
#PBS -S /bin/bash
(cd %s
    python autoZippedResultsCombiner.py %s %d "job-(\d*).zip" 10 1> WatcherReport.txt
    mv WatcherReport.txt %s
)
""" % (walltime, utilitiesFolder, resultsFolder, numberOfJobs, resultsFolder)
    )

print("Jobs generated. Submit them using submitJobs scripts.")
