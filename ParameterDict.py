from InitialConditions import initial_condition_control

controlParameterList = {
    'simulation_type'       :   'hybrid', 
    # options: 'hybrid', 'hydro', 'hydroEM', 'hydroEM_with_decaycocktail', 
    #          'hydroEM_preEquilibrium', 'hydroEM_with_decaycocktail_with_urqmd'
    'niceness'              :   0,  
    # range from 0 to 19 for process priority, 0 for the highest priority
}

superMCParameters = {
    'model_name'                    :   'MCGlb',    # MCGlb or MCKLN
    'Aproj'                         :   208,
    'Atarg'                         :   208,
    'ecm'                           :   2760,
    'finalFactor'                   :   56.763,
    'alpha'                         :   0.118,      # WN/BC mixing ratio in MCGlb
    'lambda'                        :   0.218,      # saturation scale parameter in MCKLN
    'operation'                     :   2,
    'include_NN_correlation'        :   1,
    'cc_fluctuation_model'          :   6,
    'cc_fluctuation_Gamma_theta'    :   0.75,       
    'maxx'                          :   13.0,       # grid size in x (fm)
    'maxy'                          :   13.0,       # grid size in y (fm)
    'dx'                            :   0.1,        # grid spacing in x (fm)
    'dy'                            :   0.1,        # grid spacing in y (fm)
}

# only effective when simulation_type == hydroEM_preEquilibrium
preEquilibriumParameters = {
    'event_mode'            :    1,  
    'taumin'                :    0.6,
    'taumax'                :    0.6,
    'dtau'                  :    0.2,
}

hydroParameters = {
    'vis'       :   0.08,
    'Ivisflag'  :   0,        # flag to use temperature dependent eta/s(T)
    'IvisBulkFlag'  :   0,    # flag for temperature dependence of bulk viscosity
    'visbulknorm'   :   0.0,  # the overall normalization of the bulk viscosity 
                              # (set to 0.0 for shear only simulation)
    'IviscousEqsType'  :  2,  # type of evolution equations for viscous quantities 
                              # (1: Israel-Stewart eq. 2: DNMR eq.)
    'T0'        :   0.6,      # tau_0
    'dt'        :   0.02,     # dtau
    'Edec'      :   0.18,
    'iLS'       :   130,      # lattice size in transverse plane 2*iLS+1
    'dx'        :   0.10,     # lattice spacing in x (fm) 
                              # need to be the same as dx in superMC
    'dy'        :   0.10,     # lattice spacing in y (fm)
                              # need to be the same as dy in superMC
    'IhydroJetoutput' :   1,  # switch for output hydro evolution history
    'InitialURead'    :   0,  # set it to be 1 when simulation_type == hydroEM_preEquilibrium
    'Initialpitensor' :   0,  # initialization of pi tensor
                              # 0: initialize to 0; 1: initialze to Navier-Stock value
}

hydroMusicParameters = {
    'Shear_to_S_ratio'              :   0.30,   # value of \eta/s
}

iSSParameters = {
    'hydro_mode'                    :   1,
    'turn_on_bulk'                  :   0,
    'turn_on_shear'                 :   0,
    'include_deltaf_bulk'           :   0,
    'include_deltaf_shear'          :   0,
    'calculate_vn'                  :   0,
    'MC_sampling'                   :   2,
    'number_of_repeated_sampling'   :   100,
}

photonEmissionParameters = {
    'dx'          :   0.3,
    'dy'          :   0.3,
    'dTau'        :   0.3,
    'tau_start'   :   0.6,
    'tau_end'     :   30.0,
    'T_dec'       :   0.150,
    'T_cuthigh'   :   0.8,
    'T_cutlow'    :   0.1,
    'T_sw_high'   :   0.180,
    'T_sw_low'    :   0.1795,
    'calHGIdFlag' :   0,
    'differential_flag'   :  0,
    'enable_polyakov_suppression'   :    0,
}
