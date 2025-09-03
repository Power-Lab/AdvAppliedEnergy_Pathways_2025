import datetime
import os
import sys
import json
import logging

import pandas as pd
import numpy as np

from callUtility import getWorkDir
from multiYearAutomation import MultiYearAutomation
from initData import seedHour, initCellData, initDemLayer, initModelExovar
from main import interProvinModel
from clearupData import cellResInfo, TransCap, update_storage_capacity, TransInfo, curtailed, CurtailedSplitVRE, \
    LoadProfile, obtain_output_summary, obtain_simulation_summary
from plotResult import windsolarCellMap, windsolarInstalledFactor, TransDirect, TransCapMap, TransLoadMap,\
    TransCongestion

# Step 0: Set parameters (if run remotely using shell scripts)
# optimization_days = int(sys.argv[1])  # 365
# start_year = int(sys.argv[2])  # 2050
# year_count = int(sys.argv[3])  # 1
# node = str(sys.argv[4])  # "home"
# emission_target = str(sys.argv[5])  # "2C"
# ccs_start_year = int(sys.argv[6])  # 2040
# heating_electrification = str(sys.argv[7])  # "chp_ccs"
# renewable_cost_decline = str(sys.argv[8])  # "baseline"
# endogenize_firm_capacity = str(sys.argv[9])  # 1
# demand_sensitivity = str(sys.argv[10])  # "p5"
# ccs_retrofit_cost = float(sys.argv[11])  # 3500
# custom_tag = ""

# Step 0: Set parameters (if run locally on your laptop)
optimization_days = 7
start_year = 2030
year_count = 4  # [1, 4]
node = "pc"
emission_target = "2C"  # ["2C", "15C"]
ccs_start_year = 2040  # [2040, 2050, 2060, 2070]
heating_electrification = "heat_pump"  # ["chp_ccs", "heat_pump"]
renewable_cost_decline = "baseline"  # ["baseline", "conservative"]
endogenize_firm_capacity = 0  # [0, 1]
demand_sensitivity = "p5"  # ["none", "p5", "m5"]
ccs_retrofit_cost = float(3500)  # 3500 ~ 10000
custom_tag = "heat_pump"

# Read parameters
date = datetime.date.today().strftime("%m%d")
if year_count == 1:
    res_tag = f"test_{date}_{optimization_days}days_{str(start_year)}only_{node}_{custom_tag}"
else:
    res_tag = f"test_{date}_{optimization_days}days_all_years_{node}"
year_list = [start_year + 10 * i for i in range(year_count)]

optimization_step = 1
vre_year = "w2015_s2015"
year_start = 2025
year_end = 2060
year_step = 5

# try:
#     logging.basicConfig(filename=f'/oasis/tscc/scratch/zhz121/china-re-pathways/LinearOpt_UCSD/data_res/{res_tag}.log',
#                         level=logging.INFO,
#                         format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
# except:
#     try:
#         logging.basicConfig(filename=f'../data_res/{res_tag}.log',
#                             level=logging.INFO,
#                             format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
#     except:
#         logging.basicConfig(filename=f'./china-re-pathways/LinearOpt_UCSD/data_res/{res_tag}.log',
#                             level=logging.INFO,
#                             format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

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

# Step 3: initialize exogenous parameters
for idx in range(len(multiyear_input.yr_req)):
    # Specify parameters
    curr_year = multiyear_input.yr_req[idx]
    last_year = multiyear_input.yr_req[idx - 1] if idx != 0 else 2020

    # Specify folder paths
    out_input_path = os.path.join(multiyear_input.out_path, str(curr_year), "inputs")

    # 3.1 Update and save input scenario parameters
    scen_params["scenario"]["comply_with_medium_vre_goal"] = 1
    scen_params["scenario"]["endogenize_firm_capacity"] = endogenize_firm_capacity
    scen_params["scenario"]["ccs_start_year"] = ccs_start_year
    scen_params["scenario"]["emission_target"] = emission_target
    scen_params["scenario"]["heating_electrification"] = heating_electrification
    scen_params["scenario"]["renewable_cost_decline"] = renewable_cost_decline
    scen_params["scenario"]["demand_sensitivity"] = demand_sensitivity
    scen_params["scenario"]["emission_factor_method"] = "mean"
    scen_params["ccs"]["capex_coal_ccs"] = ccs_retrofit_cost
    scen_params["ccs"]["capex_gas_ccs"] = ccs_retrofit_cost

    if scen_params["scenario"]["renewable_cost_decline"] == "baseline":
        # Baseline cost declines
        capex_on_wind_list = np.linspace(7700, 3000, len(multiyear_input.yr_req) + 1)
        capex_off_wind_list = np.linspace(15000, 5400, len(multiyear_input.yr_req) + 1)
        capex_pv_list = np.linspace(5300, 1500, len(multiyear_input.yr_req) + 1)
        capex_dpv_list = np.linspace(5300, 2000, len(multiyear_input.yr_req) + 1)
        capex_bat_list = np.linspace(6000, 2700, len(multiyear_input.yr_req) + 1)
        capex_caes_list = np.linspace(24000, 4800, len(multiyear_input.yr_req) + 1)
        capex_vrb_list = np.linspace(25600, 3000, len(multiyear_input.yr_req) + 1)
    elif scen_params["scenario"]["renewable_cost_decline"] == "conservative":
        # # Conservative cost declines based on NREL projections (2021)
        # capex_on_wind_list = [7700, 7700, 5515.8, 5515.8, 5240, 5240, 4964.2, 4964.2, 4688.4]
        # capex_off_wind_list = [15000, 15000, 11790.6, 11790.6, 10953.9, 10953.9, 10424.4, 10424.4, 9894.9]
        # capex_pv_list = [5300, 5300, 4549.5, 4549.5, 3768.1, 3768.1, 2986.8, 2986.8, 2205.4]
        # capex_dpv_list = [5300, 5300, 4421.7, 4421.7, 3582.5, 3582.5, 2743.2, 2743.2, 1904]
        # capex_bat_list = [6000, 6000, 4318.4, 4318.4, 4318.4, 4318.4, 4318.4, 4318.4, 4318.4]
        # Conservative cost declines based on NREL projections (2023)
        capex_on_wind_list = [7700, 7700, 7197.2, 7197.2, 6711.4, 6711.4, 6225.5, 6225.5, 5739.7]
        capex_off_wind_list = [15000, 15000, 13008.3, 13008.3, 12256.5, 12256.5, 11799.3, 11799.3, 11342.0]
        capex_pv_list = [5300, 5300, 4951.0, 4951.0, 4150.5, 4150.5, 3403.3, 3403.3, 2656.2]
        capex_dpv_list = [5300, 5300, 5112.7, 5112.7, 4296.8, 4296.8, 3468.9, 3468.9, 2640.9]
        capex_bat_list = [6000, 6000, 5644.6, 5644.6, 5259.0, 5259.0, 4869.6, 4869.6, 4480.2]
        capex_caes_list = np.linspace(24000, 12000, len(multiyear_input.yr_req) + 1)
        capex_vrb_list = np.linspace(25600, 12500, len(multiyear_input.yr_req) + 1)
    scen_params["vre"]["capex_equip_on_wind"] = capex_on_wind_list[idx + 1] - 800
    scen_params["vre"]["capex_om_on_wind"] = np.linspace(170, 45, len(multiyear_input.yr_req) + 1)[idx + 1]
    scen_params["vre"]["capex_equip_off_wind"] = capex_off_wind_list[idx + 1] - 1600
    scen_params["vre"]["capex_om_off_wind"] = np.linspace(715, 81, len(multiyear_input.yr_req) + 1)[idx + 1]
    scen_params["vre"]["capex_equip_pv"] = capex_pv_list[idx + 1] - 400
    scen_params["vre"]["capex_om_pv"] = np.linspace(85, 7.5, len(multiyear_input.yr_req) + 1)[idx + 1]
    scen_params["vre"]["capex_equip_dpv"] = capex_dpv_list[idx + 1] - 600
    scen_params["vre"]["capex_om_dpv"] = np.linspace(107, 10, len(multiyear_input.yr_req) + 1)[idx + 1]
    scen_params['storage']['capex_power_phs'] = np.linspace(3840, 3840, len(multiyear_input.yr_req) + 1)[idx + 1]
    scen_params['storage']['capex_power_bat'] = capex_bat_list[idx + 1]
    scen_params['storage']['capex_power_lds']['caes'] = capex_caes_list[idx + 1]
    scen_params['storage']['capex_power_lds']['vrb'] = capex_vrb_list[idx + 1]

    # 3.2 Initialize optimization hours
    scen_params["optimization_hours"]["step"] = optimization_step
    scen_params["optimization_hours"]["days"] = optimization_days
    seedHour(vre_year=vre_year,
             years=scen_params["optimization_hours"]["years"],
             step=scen_params["optimization_hours"]["step"],
             days=scen_params["optimization_hours"]["days"],
             res_tag=res_tag, curr_year=curr_year)
    hour_seed = pd.read_csv(os.path.join(out_input_path, "hour_seed.csv"), header=None).iloc[:, 0].to_list()

    # Save the updated scenario parameters
    with open(os.path.join(out_input_path, "scen_params.json"), 'w') as fp:
        json.dump(scen_params, fp)

    # 3.3 Initialize demand layers
    initDemLayer(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year, scen_params=scen_params)

# Step 4: initialize parameters that have endogenous elements
# Only run optimization per 10 years, hence the break-up from previous steps
for idx in range(len(year_list)):
    # Specify parameters
    curr_year = year_list[idx]
    # last_year = year_list[idx - 1] if idx != 0 else 2020
    last_year = curr_year - 10

    # Specify folder paths
    out_input_path = os.path.join(multiyear_input.out_path, str(curr_year), "inputs")

    # Read scenario parameters and optimization hours
    hour_seed = pd.read_csv(os.path.join(out_input_path, "hour_seed.csv"), header=None).iloc[:, 0].to_list()
    with open(os.path.join(out_input_path, "scen_params.json")) as f:
        scen_params = json.load(f)

    # 4.1 Initialize VRE cell data
    for vre in ["solar", "wind"]:
        initCellData(vre=vre, vre_year_single="2015", hour_seed=hour_seed, res_tag=res_tag, vre_year=vre_year,
                     curr_year=curr_year, last_year=last_year, scen_params=scen_params)

    # 4.2 Initialize layer capacity
    initModelExovar(vre_year=vre_year, res_tag=res_tag,
                    curr_year=curr_year, last_year=last_year, scen_params=scen_params)

    # Step 5: run optimization for the current year
    interProvinModel(vre_year=vre_year, res_tag=res_tag, init_data=0, is8760=0,
                     curr_year=curr_year, scen_params=scen_params)

    # Step 6: post-process optimization outputs
    cellResInfo(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    TransCap(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    update_storage_capacity(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    TransInfo(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    curtailed(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year, re="wind")
    curtailed(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year, re="solar")
    # CurtailedSplitVRE(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    # LoadProfile(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)

    # Step 7: plot outputs
    # windsolarInstalledFactor(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    # windsolarCellMap(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    # TransCapMap(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    # TransDirect(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)
    # TransLoadMap(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year, transKind="bi")
    # TransLoadMap(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year, transKind="net")
    # TransCongestion(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)

    # Step 8: obtain provincial and national output summary
    obtain_output_summary(vre_year=vre_year, res_tag=res_tag, curr_year=curr_year)

# Step 9: obtain provincial and national output summary for the whole simulation years
if len(year_list) >= 4:
    obtain_simulation_summary(vre_year=vre_year, res_tag=res_tag, year_list=year_list)

# Step 10: remove excessive huge files
for idx in range(len(multiyear_input.yr_req)):
    try:
        # Specify folder paths
        curr_year = multiyear_input.yr_req[idx]
        out_input_path = os.path.join(multiyear_input.out_path, str(curr_year), "inputs")
        print(out_input_path)

        # Delete VRE cell pickle files due to storage space limits
        os.remove(os.path.join(out_input_path, "solar_cell.pkl"))
        os.remove(os.path.join(out_input_path, "wind_cell.pkl"))
    except:
        pass
