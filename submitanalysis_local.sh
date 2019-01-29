#!/bin/bash
NJOBS=$1
NEVTPERJOB=$2

NCENTRALITIES=1
CENTRALITIES=( "30-40" )
HIGHEREVTNOS=( 3334 )
TAG=`date +%Y%m%d%H%M`

for ((i=0;i<$NCENTRALITIES;++i))  
do
CENTRALITY=${CENTRALITIES[i]}
HIGHEREVTNO=${HIGHEREVTNOS[i]}
cat > InitialConditions.py <<EOF
initial_condition_control = {
    'centrality': '$CENTRALITY%',  # centrality bin
    'cut_type': 'total_entropy',
    # centrality cut variable: total_entropy or Npart
    'initial_condition_type': 'pre-generated',
    # type of initial conditions: superMC or pre-generated
    'pre-generated_initial_file_path': '../IPGLASMA',
    # file path for the pre-generated initial condition files
    'pre-generated_initial_file_pattern': 'epsilon-u-Hydro[1-$HIGHEREVTNO].dat',  
    # name pattern for the initial condition files
    'pre-generated_initial_file_read_in_mode': 3, 
    # 2: read in mode for VISH2+1, 3: read in mode for IP Glasma
}
EOF

./generateJobs_local.py $NJOBS $NEVTPERJOB ./$TAG/PlayGround$CENTRALITY ./$TAG/RESULTS$CENTRALITY 06:00:00
sleep 2
./submitJobs_local.py
sleep 4

done
