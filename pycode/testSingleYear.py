import os
import json

import pandas as pd

from callUtility import getWorkDir
from multiYearAutomation import MultiYearAutomation
from initData import seedHour, initCellData, initDemLayer, initModelExovar
from main import interProvinModel
from clearupData import cellResInfo, TransCap, update_storage_capacity

# Step 0: Set parameters (if run locally on your laptop)
res_tag = "test_single_year"
vre_year = "w2015_s2015"
year_start = 2025
year_end = 2060
year_step = 5
year_list = [2060]  # Specify the list of years for running optimization

optimization_days = 10
optimization_step = 5
emission_target = "2C"
demand_sensitivity = "p5"

# Step 1: generate multi-year inputs
multiyear_input = MultiYearAutomation(yr_start=year_start,
                                      yr_end=year_end,
                                      yr_step=year_step,
                                      res_tag=res_tag,
                                      vre_year=vre_year,
                                      emission_target=emission_target,
                                      demand_sensitivity=demand_sensitivity
                                      )
multiyear_input.automate_inputs()

# Step 2: read the template of scenario parameters
work_dir = getWorkDir()
with open(os.path.join(work_dir, "data_csv", "scen_params_template.json")) as f:
    scen_params = json.load(f)
f.close()

# Step 3: initialize parameters that have endogenous elements
for idx in range(len(year_list)):
    # Specify parameters
    curr_year = year_list[idx]
    last_year = year_list[idx - 1] if idx != 0 else 2020

    # Specify folder paths
    out_input_path = os.path.join(multiyear_input.out_path, str(curr_year), "inputs")

    # Initialize scenario parameters and optimization hours
    scen_params["optimization_hours"]["step"] = optimization_step
    scen_params["optimization_hours"]["days"] = optimization_days
    with open(os.path.join(out_input_path, "scen_params.json"), 'w') as fp:
        json.dump(scen_params, fp)
    seedHour(vre_year=vre_year,
             years=scen_params["optimization_hours"]["years"],
             step=scen_params["optimization_hours"]["step"],
             days=scen_params["optimization_hours"]["days"],
             res_tag=res_tag, curr_year=curr_year)
    hour_seed = pd.read_csv(os.path.join(out_input_path, "hour_seed.csv"),
                            header=None).iloc[:, 0].to_list()

    # Initialize demand layers
    initDemLayer(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year, scen_params=scen_params)

    # Initialize VRE cell data
    for vre in ["solar", "wind"]:
        initCellData(vre=vre, vre_year_single="2015", hour_seed=hour_seed, res_tag=res_tag, vre_year=vre_year,
                     curr_year=curr_year, last_year=last_year, scen_params=scen_params)

    # Initialize layer capacity
    initModelExovar(vre_year=vre_year, res_tag=res_tag,
                    curr_year=curr_year, last_year=last_year, scen_params=scen_params)

    # Step 4: run optimization for the current year
    interProvinModel(vre_year=vre_year, res_tag=res_tag, init_data=0, is8760=0,
                     curr_year=curr_year, scen_params=scen_params)

    # Step 5: post-process optimization outputs
    cellResInfo(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    TransCap(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    update_storage_capacity(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
