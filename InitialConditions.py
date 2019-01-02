initial_condition_control = {
    'centrality': '30-40%',  # centrality bin
    'cut_type': 'total_entropy',
    # centrality cut variable: total_entropy or Npart
    'initial_condition_type': 'pre-generated',
    # type of initial conditions: superMC or pre-generated
    'pre-generated_initial_file_path': '../IPGLASMA',
    # file path for the pre-generated initial condition files
    'pre-generated_initial_file_pattern': 'epsilon-u-Hydro[1-3334].dat',  
    # name pattern for the initial condition files
    'pre-generated_initial_file_read_in_mode': 3, 
    # 2: read in mode for VISH2+1, 3: read in mode for IP Glasma
}
