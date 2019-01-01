#!/bin/bash
NJOBS=$1
NEVTPERJOB=$2

NCENTRALITIES=10
CENTRALITIES=( "0-10" "10-20" "20-30" "30-40" "40-50" "50-60" "60-70" "70-80" "80-90" "90-100" )
HIGHEREVTNOS=( 3970 3970 3254 3334 3260 3280 3334 3285 3334 3238 )

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
    'pre-generated_initial_file_path': '../../vgonzale/IPGLASMA',
    # file path for the pre-generated initial condition files
    'pre-generated_initial_file_pattern': 'epsilon-u-Hydro[1-$HIGHEREVTNO].dat',  
    # name pattern for the initial condition files
    'pre-generated_initial_file_read_in_mode': 3, 
    # 2: read in mode for VISH2+1, 3: read in mode for IP Glasma
}
EOF

./generateJobs_slurm.py $NJOBS $NEVTPERJOB ./PlayGround$CENTRALITY ./RESULTS$CENTRALITY
sleep 2
./submitJobs_slurm.py
sleep 4

done
